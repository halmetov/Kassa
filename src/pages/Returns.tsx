import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { toast } from "sonner";
import { Search } from "lucide-react";

export default function Returns() {
  const [searchSaleId, setSearchSaleId] = useState("");
  const [sale, setSale] = useState<any>(null);
  const [saleItems, setSaleItems] = useState<any[]>([]);
  const [returnItems, setReturnItems] = useState<Map<string, number>>(new Map());
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  const searchSale = async () => {
    if (!searchSaleId.trim()) {
      toast.error("Введите ID чека");
      return;
    }

    const { data: saleData } = await supabase
      .from('sales')
      .select(`
        *,
        employees (name),
        branches (name),
        clients (name, id)
      `)
      .eq('id', searchSaleId)
      .maybeSingle();

    if (!saleData) {
      toast.error("Чек не найден");
      return;
    }

    setSale(saleData);

    const { data: itemsData } = await supabase
      .from('sale_items')
      .select(`
        *,
        products (name, unit)
      `)
      .eq('sale_id', searchSaleId);

    if (itemsData) {
      setSaleItems(itemsData);
      setReturnItems(new Map());
    }
  };

  const updateReturnQuantity = (itemId: string, maxQty: number, value: number) => {
    const newMap = new Map(returnItems);
    const qty = Math.min(Math.max(0, value), maxQty);
    
    if (qty > 0) {
      newMap.set(itemId, qty);
    } else {
      newMap.delete(itemId);
    }
    
    setReturnItems(newMap);
  };

  const getTotalReturnAmount = () => {
    return saleItems.reduce((sum, item) => {
      const returnQty = returnItems.get(item.id) || 0;
      return sum + (returnQty * parseFloat(item.price));
    }, 0);
  };

  const handleReturn = async () => {
    if (returnItems.size === 0) {
      toast.error("Выберите товары для возврата");
      return;
    }

    try {
      // Return items to stock
      for (const [itemId, returnQty] of returnItems.entries()) {
        const item = saleItems.find(i => i.id === itemId);
        if (item) {
          const { data: product } = await supabase
            .from('products')
            .select('quantity')
            .eq('id', item.product_id)
            .single();
          
          if (product) {
            await supabase
              .from('products')
              .update({ quantity: (product.quantity || 0) + returnQty })
              .eq('id', item.product_id);
          }
        }
      }

      // Update client debt if credit was used
      if (sale.credit_amount > 0 && sale.client_id) {
        const returnAmount = getTotalReturnAmount();
        const creditPortion = (returnAmount / parseFloat(sale.total_amount)) * parseFloat(sale.credit_amount);
        
        const { data: client } = await supabase
          .from('clients')
          .select('debt')
          .eq('id', sale.client_id)
          .single();
        
        if (client) {
          await supabase
            .from('clients')
            .update({ debt: Math.max(0, (client.debt || 0) - creditPortion) })
            .eq('id', sale.client_id);
        }
      }

      toast.success("Возврат выполнен успешно");
      setSale(null);
      setSaleItems([]);
      setReturnItems(new Map());
      setSearchSaleId("");
      setShowConfirmModal(false);
    } catch (error) {
      toast.error("Ошибка при возврате");
      console.error(error);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Возврат</h1>
        <p className="text-muted-foreground">Возврат товаров</p>
      </div>

      <Card className="p-6">
        <div className="flex gap-2 mb-6">
          <Input
            placeholder="ID чека"
            value={searchSaleId}
            onChange={(e) => setSearchSaleId(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && searchSale()}
          />
          <Button onClick={searchSale}>
            <Search className="h-4 w-4 mr-2" />
            Найти
          </Button>
        </div>

        {sale && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">Дата:</span>{" "}
                {new Date(sale.created_at).toLocaleString('ru-RU')}
              </div>
              <div>
                <span className="text-muted-foreground">Сотрудник:</span>{" "}
                {sale.employees?.name || "-"}
              </div>
              <div>
                <span className="text-muted-foreground">Филиал:</span>{" "}
                {sale.branches?.name || "-"}
              </div>
              <div>
                <span className="text-muted-foreground">Сумма:</span>{" "}
                <span className="font-bold">{parseFloat(sale.total_amount).toFixed(2)} ₸</span>
              </div>
            </div>

            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Товар</TableHead>
                  <TableHead className="text-right">Продано</TableHead>
                  <TableHead className="text-right">Цена</TableHead>
                  <TableHead className="text-right">Вернуть</TableHead>
                  <TableHead className="text-right">Сумма возврата</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {saleItems.map((item) => {
                  const returnQty = returnItems.get(item.id) || 0;
                  const returnAmount = returnQty * parseFloat(item.price);
                  
                  return (
                    <TableRow key={item.id}>
                      <TableCell>{item.products?.name}</TableCell>
                      <TableCell className="text-right">
                        {item.quantity} {item.products?.unit}
                      </TableCell>
                      <TableCell className="text-right">
                        {parseFloat(item.price).toFixed(2)} ₸
                      </TableCell>
                      <TableCell>
                        <Input
                          type="number"
                          min="0"
                          max={item.quantity}
                          value={returnQty}
                          onChange={(e) => 
                            updateReturnQuantity(item.id, item.quantity, parseInt(e.target.value) || 0)
                          }
                          className="w-24 ml-auto"
                        />
                      </TableCell>
                      <TableCell className="text-right font-medium">
                        {returnAmount.toFixed(2)} ₸
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>

            <div className="flex justify-between items-center border-t pt-4">
              <div className="text-xl font-bold">
                Итого к возврату: {getTotalReturnAmount().toFixed(2)} ₸
              </div>
              <Button
                onClick={() => setShowConfirmModal(true)}
                disabled={returnItems.size === 0}
              >
                Выполнить возврат
              </Button>
            </div>
          </div>
        )}
      </Card>

      <Dialog open={showConfirmModal} onOpenChange={setShowConfirmModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Подтверждение возврата</DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            <p>Вы уверены, что хотите выполнить возврат на сумму {getTotalReturnAmount().toFixed(2)} ₸?</p>
            
            <ul className="text-sm space-y-1">
              {Array.from(returnItems.entries()).map(([itemId, qty]) => {
                const item = saleItems.find(i => i.id === itemId);
                return (
                  <li key={itemId}>
                    • {item?.products?.name}: {qty} {item?.products?.unit}
                  </li>
                );
              })}
            </ul>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowConfirmModal(false)}>
              Отмена
            </Button>
            <Button onClick={handleReturn}>Подтвердить</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
