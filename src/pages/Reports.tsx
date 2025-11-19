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
} from "@/components/ui/dialog";
import { Eye } from "lucide-react";

export default function Reports() {
  const [sales, setSales] = useState<any[]>([]);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [selectedSale, setSelectedSale] = useState<any>(null);
  const [saleItems, setSaleItems] = useState<any[]>([]);
  const [showDetailsModal, setShowDetailsModal] = useState(false);

  useEffect(() => {
    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - 30);
    
    setEndDate(end.toISOString().split('T')[0]);
    setStartDate(start.toISOString().split('T')[0]);
    
    fetchSales(start, end);
  }, []);

  const fetchSales = async (start?: Date, end?: Date) => {
    let query = supabase
      .from('sales')
      .select(`
        *,
        employees (name),
        branches (name),
        clients (name)
      `)
      .order('created_at', { ascending: false });

    if (start) {
      query = query.gte('created_at', start.toISOString());
    }
    if (end) {
      const endOfDay = new Date(end);
      endOfDay.setHours(23, 59, 59, 999);
      query = query.lte('created_at', endOfDay.toISOString());
    }

    const { data } = await query;
    if (data) setSales(data);
  };

  const handleFilter = () => {
    if (startDate && endDate) {
      fetchSales(new Date(startDate), new Date(endDate));
    }
  };

  const viewDetails = async (sale: any) => {
    setSelectedSale(sale);
    
    const { data } = await supabase
      .from('sale_items')
      .select(`
        *,
        products (name, unit)
      `)
      .eq('sale_id', sale.id);
    
    if (data) setSaleItems(data);
    setShowDetailsModal(true);
  };

  const getTotalSales = () => {
    return sales.reduce((sum, sale) => sum + parseFloat(sale.total_amount), 0);
  };

  const getTotalCash = () => {
    return sales.reduce((sum, sale) => sum + parseFloat(sale.cash_amount || 0), 0);
  };

  const getTotalCard = () => {
    return sales.reduce((sum, sale) => sum + parseFloat(sale.card_amount || 0), 0);
  };

  const getTotalCredit = () => {
    return sales.reduce((sum, sale) => sum + parseFloat(sale.credit_amount || 0), 0);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Отчеты</h1>
        <p className="text-muted-foreground">История продаж</p>
      </div>

      <Card className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div>
            <Label>Дата начала</Label>
            <Input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </div>
          <div>
            <Label>Дата окончания</Label>
            <Input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </div>
          <div className="flex items-end">
            <Button onClick={handleFilter} className="w-full">
              Применить фильтр
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card className="p-4">
            <div className="text-sm text-muted-foreground">Всего продаж</div>
            <div className="text-2xl font-bold">{getTotalSales().toFixed(2)} ₸</div>
          </Card>
          <Card className="p-4">
            <div className="text-sm text-muted-foreground">Наличные</div>
            <div className="text-2xl font-bold">{getTotalCash().toFixed(2)} ₸</div>
          </Card>
          <Card className="p-4">
            <div className="text-sm text-muted-foreground">Карта</div>
            <div className="text-2xl font-bold">{getTotalCard().toFixed(2)} ₸</div>
          </Card>
          <Card className="p-4">
            <div className="text-sm text-muted-foreground">В долг</div>
            <div className="text-2xl font-bold">{getTotalCredit().toFixed(2)} ₸</div>
          </Card>
        </div>

        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Дата</TableHead>
              <TableHead>Сотрудник</TableHead>
              <TableHead>Филиал</TableHead>
              <TableHead>Клиент</TableHead>
              <TableHead className="text-right">Сумма</TableHead>
              <TableHead className="text-right">Наличные</TableHead>
              <TableHead className="text-right">Карта</TableHead>
              <TableHead className="text-right">Долг</TableHead>
              <TableHead></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sales.map((sale) => (
              <TableRow key={sale.id}>
                <TableCell>
                  {new Date(sale.created_at).toLocaleString('ru-RU')}
                </TableCell>
                <TableCell>{sale.employees?.name || "-"}</TableCell>
                <TableCell>{sale.branches?.name || "-"}</TableCell>
                <TableCell>{sale.clients?.name || "-"}</TableCell>
                <TableCell className="text-right font-medium">
                  {parseFloat(sale.total_amount).toFixed(2)} ₸
                </TableCell>
                <TableCell className="text-right">
                  {parseFloat(sale.cash_amount || 0).toFixed(2)} ₸
                </TableCell>
                <TableCell className="text-right">
                  {parseFloat(sale.card_amount || 0).toFixed(2)} ₸
                </TableCell>
                <TableCell className="text-right">
                  {parseFloat(sale.credit_amount || 0).toFixed(2)} ₸
                </TableCell>
                <TableCell>
                  <Button
                    size="icon"
                    variant="ghost"
                    onClick={() => viewDetails(sale)}
                  >
                    <Eye className="h-4 w-4" />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      <Dialog open={showDetailsModal} onOpenChange={setShowDetailsModal}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Детали продажи</DialogTitle>
          </DialogHeader>

          {selectedSale && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">Дата:</span>{" "}
                  {new Date(selectedSale.created_at).toLocaleString('ru-RU')}
                </div>
                <div>
                  <span className="text-muted-foreground">Сотрудник:</span>{" "}
                  {selectedSale.employees?.name || "-"}
                </div>
                <div>
                  <span className="text-muted-foreground">Филиал:</span>{" "}
                  {selectedSale.branches?.name || "-"}
                </div>
                <div>
                  <span className="text-muted-foreground">Клиент:</span>{" "}
                  {selectedSale.clients?.name || "-"}
                </div>
              </div>

              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Товар</TableHead>
                    <TableHead className="text-right">Количество</TableHead>
                    <TableHead className="text-right">Цена</TableHead>
                    <TableHead className="text-right">Сумма</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {saleItems.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell>{item.products?.name}</TableCell>
                      <TableCell className="text-right">
                        {item.quantity} {item.products?.unit}
                      </TableCell>
                      <TableCell className="text-right">
                        {parseFloat(item.price).toFixed(2)} ₸
                      </TableCell>
                      <TableCell className="text-right font-medium">
                        {parseFloat(item.total).toFixed(2)} ₸
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              <div className="border-t pt-4 space-y-2">
                <div className="flex justify-between">
                  <span>Наличные:</span>
                  <span>{parseFloat(selectedSale.cash_amount || 0).toFixed(2)} ₸</span>
                </div>
                <div className="flex justify-between">
                  <span>Карта:</span>
                  <span>{parseFloat(selectedSale.card_amount || 0).toFixed(2)} ₸</span>
                </div>
                <div className="flex justify-between">
                  <span>В долг:</span>
                  <span>{parseFloat(selectedSale.credit_amount || 0).toFixed(2)} ₸</span>
                </div>
                <div className="flex justify-between text-xl font-bold border-t pt-2">
                  <span>Итого:</span>
                  <span>{parseFloat(selectedSale.total_amount).toFixed(2)} ₸</span>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
