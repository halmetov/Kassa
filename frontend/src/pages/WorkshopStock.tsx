import { useEffect, useState } from "react";
import { apiGet } from "@/api/client";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

interface StockItem {
  product_id: number;
  name: string;
  quantity: number;
  unit?: string;
  barcode?: string;
}

export default function WorkshopStock() {
  const [items, setItems] = useState<StockItem[]>([]);
  const [search, setSearch] = useState("");

  const load = async () => {
    try {
      const data = await apiGet<StockItem[]>(`/api/workshop/products${search ? `?search=${encodeURIComponent(search)}` : ""}`);
      setItems(data);
    } catch (error: any) {
      toast.error(error?.message || "Не удалось загрузить склад");
    }
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="grid gap-4">
      <div className="flex gap-2">
        <Input placeholder="Поиск по названию или штрихкоду" value={search} onChange={(e) => setSearch(e.target.value)} />
        <Button onClick={load}>Поиск</Button>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Склад (Цех)</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {items.map((item) => (
            <div key={item.product_id} className="border p-2 rounded">
              <div className="font-semibold">{item.name}</div>
              <div className="text-sm text-muted-foreground">{item.barcode}</div>
              <div className="text-sm">Остаток: {item.quantity} {item.unit}</div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
