import { useEffect, useState } from "react";
import { apiGet, apiPost } from "@/api/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { toast } from "sonner";

interface IncomeProduct {
  id: number;
  name: string;
  unit?: string;
  barcode?: string;
  photo?: string;
}

interface StockItem {
  product_id: number;
  name: string;
  available_qty: number;
  unit?: string;
  barcode?: string;
  photo?: string;
}

interface WorkshopIncomeResponse {
  income: {
    id: number;
  };
  stock: { product_id: number; branch_id: number; quantity: number }[];
}

export default function WorkshopIncome() {
  const [productQuery, setProductQuery] = useState("");
  const [productOptions, setProductOptions] = useState<IncomeProduct[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<IncomeProduct | null>(null);
  const [quantity, setQuantity] = useState("1");
  const [purchasePrice, setPurchasePrice] = useState("0");
  const [salePrice, setSalePrice] = useState("0");
  const [stock, setStock] = useState<StockItem[]>([]);

  const loadStock = async () => {
    try {
      const data = await apiGet<StockItem[]>("/api/workshop/stock");
      setStock(data);
    } catch (error: any) {
      toast.error(error?.message || "Не удалось загрузить склад цеха");
    }
  };

  const searchProducts = async (query: string) => {
    if (!query || query.length < 2) {
      setProductOptions([]);
      return;
    }
    try {
      const data = await apiGet<IncomeProduct[]>(`/api/workshop/income/products?q=${encodeURIComponent(query)}`);
      setProductOptions(data);
    } catch (error: any) {
      toast.error(error?.message || "Не удалось найти товары");
    }
  };

  useEffect(() => {
    loadStock();
  }, []);

  useEffect(() => {
    const handle = setTimeout(() => searchProducts(productQuery), 300);
    return () => clearTimeout(handle);
  }, [productQuery]);

  const submitIncome = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!selectedProduct) {
      toast.error("Выберите товар для прихода");
      return;
    }
    try {
      await apiPost<WorkshopIncomeResponse>("/api/workshop/income", {
        items: [
          {
            product_id: selectedProduct.id,
            quantity: Number(quantity) || 0,
            purchase_price: Number(purchasePrice) || 0,
            sale_price: Number(salePrice) || 0,
          },
        ],
      });
      toast.success("Приход сохранен");
      setSelectedProduct(null);
      setProductQuery("");
      setQuantity("1");
      loadStock();
    } catch (error: any) {
      toast.error(error?.message || "Не удалось сохранить приход");
    }
  };

  return (
    <div className="grid gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Приход (Цех)</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="grid gap-4" onSubmit={submitIncome}>
            <div className="space-y-2">
              <Input
                placeholder="Поиск товара по названию или штрихкоду"
                value={productQuery}
                onChange={(e) => setProductQuery(e.target.value)}
              />
              {productOptions.length > 0 && (
                <div className="border rounded p-2 space-y-1 max-h-48 overflow-y-auto">
                  {productOptions.map((product) => (
                    <div
                      key={product.id}
                      className="cursor-pointer p-2 rounded hover:bg-muted"
                      onClick={() => {
                        setSelectedProduct(product);
                        setProductQuery(product.name);
                        setProductOptions([]);
                      }}
                    >
                      <div className="font-semibold">{product.name}</div>
                      <div className="text-xs text-muted-foreground">{product.barcode}</div>
                    </div>
                  ))}
                </div>
              )}
              {selectedProduct && (
                <div className="text-sm text-muted-foreground">
                  Выбрано: {selectedProduct.name} {selectedProduct.barcode ? `(${selectedProduct.barcode})` : ""}
                </div>
              )}
            </div>
            <div className="grid md:grid-cols-3 gap-3">
              <Input
                type="number"
                min={0}
                step="1"
                placeholder="Количество"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                required
              />
              <Input
                type="number"
                step="0.01"
                placeholder="Закупочная цена"
                value={purchasePrice}
                onChange={(e) => setPurchasePrice(e.target.value)}
                required
              />
              <Input
                type="number"
                step="0.01"
                placeholder="Розничная цена"
                value={salePrice}
                onChange={(e) => setSalePrice(e.target.value)}
                required
              />
            </div>
            <Button type="submit">Сохранить приход</Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Остатки Цеха</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Товар</TableHead>
                <TableHead>Штрихкод</TableHead>
                <TableHead>Остаток</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {stock.map((item) => (
                <TableRow key={item.product_id}>
                  <TableCell>{item.name}</TableCell>
                  <TableCell className="text-muted-foreground">{item.barcode || ""}</TableCell>
                  <TableCell>
                    {item.available_qty} {item.unit}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
