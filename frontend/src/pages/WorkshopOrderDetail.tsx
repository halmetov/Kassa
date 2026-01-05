import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { apiGet, apiPost, apiPut } from "@/api/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";

interface Material {
  id: number;
  product_id: number;
  quantity: number;
  unit?: string;
}

interface Payout {
  id: number;
  employee_id: number;
  amount: number;
  note?: string;
  created_at?: string;
}

interface Order {
  id: number;
  title: string;
  description?: string;
  amount: number;
  status: string;
  customer_name?: string;
  materials: Material[];
  payouts: Payout[];
  closed_at?: string | null;
}

export default function WorkshopOrderDetail() {
  const { id } = useParams();
  const orderId = Number(id);
  const [order, setOrder] = useState<Order | null>(null);
  const [materialProductId, setMaterialProductId] = useState("");
  const [materialQty, setMaterialQty] = useState("0");
  const [paymentEmployee, setPaymentEmployee] = useState("");
  const [paymentAmount, setPaymentAmount] = useState("0");
  const [paymentNote, setPaymentNote] = useState("");
  const [paidAmount, setPaidAmount] = useState("0");
  const [closeNote, setCloseNote] = useState("");

  const load = async () => {
    try {
      const data = await apiGet<Order>(`/api/workshop/orders/${orderId}`);
      const materials = await apiGet<Material[]>(`/api/workshop/orders/${orderId}/materials`);
      const payouts = await apiGet<Payout[]>(`/api/workshop/orders/${orderId}/payouts`);
      setOrder({ ...data, materials, payouts });
    } catch (error: any) {
      toast.error(error?.message || "Не удалось загрузить заказ");
    }
  };

  useEffect(() => {
    if (orderId) {
      load();
    }
  }, [orderId]);

  const addMaterial = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await apiPost(`/api/workshop/orders/${orderId}/materials`, {
        product_id: Number(materialProductId),
        quantity: Number(materialQty),
      });
      toast.success("Материал добавлен");
      setMaterialProductId("");
      setMaterialQty("0");
      load();
    } catch (error: any) {
      toast.error(error?.message || "Ошибка при добавлении материала");
    }
  };

  const addPayout = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await apiPost(`/api/workshop/orders/${orderId}/payouts`, {
        employee_id: Number(paymentEmployee),
        amount: Number(paymentAmount),
        note: paymentNote || undefined,
      });
      toast.success("Выплата добавлена");
      setPaymentEmployee("");
      setPaymentAmount("0");
      setPaymentNote("");
      load();
    } catch (error: any) {
      toast.error(error?.message || "Ошибка при добавлении выплаты");
    }
  };

  const closeOrder = async () => {
    try {
      await apiPost(`/api/workshop/orders/${orderId}/close`, {
        paid_amount: Number(paidAmount),
        note: closeNote || undefined,
      });
      toast.success("Заказ закрыт");
      load();
    } catch (error: any) {
      toast.error(error?.message || "Не удалось закрыть заказ");
    }
  };

  const updateOrder = async () => {
    if (!order) return;
    try {
      await apiPut(`/api/workshop/orders/${orderId}`, {
        title: order.title,
        amount: order.amount,
        description: order.description,
        customer_name: order.customer_name,
      });
      toast.success("Заказ обновлен");
    } catch (error: any) {
      toast.error(error?.message || "Не удалось обновить заказ");
    }
  };

  if (!order) return <div>Загрузка...</div>;

  const isClosed = order.status === "closed";

  return (
    <div className="grid gap-6">
      <Card>
        <CardHeader>
          <CardTitle>{order.title}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div>Статус: {order.status}</div>
          <Input value={order.title} onChange={(e) => setOrder({ ...order, title: e.target.value })} />
          <Input type="number" value={order.amount} onChange={(e) => setOrder({ ...order, amount: Number(e.target.value) })} />
          <Textarea
            value={order.description || ""}
            onChange={(e) => setOrder({ ...order, description: e.target.value })}
            placeholder="Описание"
          />
          <Button onClick={updateOrder} disabled={isClosed}>
            Сохранить
          </Button>
          {!isClosed && (
            <div className="flex gap-2 items-center">
              <Input
                placeholder="Оплачено"
                type="number"
                value={paidAmount}
                onChange={(e) => setPaidAmount(e.target.value)}
              />
              <Input placeholder="Комментарий" value={closeNote} onChange={(e) => setCloseNote(e.target.value)} />
              <Button variant="secondary" onClick={closeOrder}>
                Завершить
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid md:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Материалы</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {!isClosed && (
              <form className="space-y-2" onSubmit={addMaterial}>
                <Input
                  placeholder="ID товара"
                  value={materialProductId}
                  onChange={(e) => setMaterialProductId(e.target.value)}
                  required
                />
                <Input
                  placeholder="Количество"
                  value={materialQty}
                  type="number"
                  step="0.01"
                  onChange={(e) => setMaterialQty(e.target.value)}
                />
                <Button type="submit">Добавить материал</Button>
              </form>
            )}
            <div className="space-y-2">
              {order.materials?.map((material) => (
                <div key={material.id} className="border p-2 rounded text-sm">
                  Товар #{material.product_id} • {material.quantity}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Выплаты</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {!isClosed && (
              <form className="space-y-2" onSubmit={addPayout}>
                <Input
                  placeholder="ID сотрудника"
                  value={paymentEmployee}
                  onChange={(e) => setPaymentEmployee(e.target.value)}
                  required
                />
                <Input
                  placeholder="Сумма"
                  value={paymentAmount}
                  type="number"
                  step="0.01"
                  onChange={(e) => setPaymentAmount(e.target.value)}
                />
                <Textarea placeholder="Заметка" value={paymentNote} onChange={(e) => setPaymentNote(e.target.value)} />
                <Button type="submit">Добавить выплату</Button>
              </form>
            )}
            <div className="space-y-2">
              {order.payouts?.map((payment) => (
                <div key={payment.id} className="border p-2 rounded text-sm">
                  Сотрудник #{payment.employee_id} • {payment.amount} •
                  {payment.created_at ? ` ${new Date(payment.created_at).toLocaleDateString()}` : ""}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
