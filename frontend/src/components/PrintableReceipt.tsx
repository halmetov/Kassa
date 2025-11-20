import { useRef } from "react";
import logo from "@/assets/logo.png";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { QRCodeCanvas } from "qrcode.react";

type SaleItem = {
  id: number;
  product_name?: string | null;
  product_id: number;
  quantity: number;
  price: number;
  product_unit?: string | null;
};

type SaleDetail = {
  id: number;
  created_at: string;
  branch_name?: string | null;
  branch_address?: string | null;
  seller_name?: string | null;
  client_name?: string | null;
  total: number;
  cash: number;
  kaspi: number;
  credit: number;
  payment_type: string;
  items: SaleItem[];
};

export function PrintableReceipt({ sale }: { sale: SaleDetail }) {
  const printRef = useRef<HTMLDivElement>(null);

  const handlePrint = () => {
    if (!printRef.current) return;
    const printWindow = window.open("", "PRINT", "width=400,height=600");
    if (!printWindow) return;
    printWindow.document.write("<html><head><title>Чек</title>");
    printWindow.document.write(
      `<style>
        body { font-family: Arial, sans-serif; padding: 12px; }
        .receipt { width: 320px; }
        .header { text-align: center; }
        .items { width: 100%; border-collapse: collapse; }
        .items th, .items td { text-align: left; padding: 4px 0; font-size: 12px; }
        .items th { border-bottom: 1px solid #ccc; }
        .totals { margin-top: 8px; font-size: 13px; }
        .meta { font-size: 12px; color: #555; }
        .qr { text-align: center; margin-top: 12px; }
      </style>`
    );
    printWindow.document.write("</head><body>");
    printWindow.document.write(printRef.current.innerHTML);
    printWindow.document.write("</body></html>");
    printWindow.document.close();
    printWindow.focus();
    printWindow.print();
  };

  const totalPaid = sale.cash + sale.kaspi;

  return (
    <div className="space-y-2">
      <Card className="p-4" ref={printRef}>
        <div className="receipt">
          <div className="header space-y-2">
            <img src={logo} alt="Logo" className="mx-auto h-10" />
            <div className="font-semibold">{sale.branch_name || "Филиал"}</div>
            <div className="text-xs text-muted-foreground">{sale.branch_address || "Адрес не указан"}</div>
            <div className="text-xs">Чек № {sale.id}</div>
            <div className="text-xs">{new Date(sale.created_at).toLocaleString("ru-RU")}</div>
          </div>

          <table className="items mt-3">
            <thead>
              <tr>
                <th>Товар</th>
                <th style={{ textAlign: "right" }}>Сумма</th>
              </tr>
            </thead>
            <tbody>
              {sale.items.map((item) => (
                <tr key={item.id}>
                  <td>
                    <div className="font-medium text-sm">{item.product_name || `ID ${item.product_id}`}</div>
                    <div className="text-xs text-muted-foreground">
                      {item.quantity} {item.product_unit || "шт"} x {item.price.toFixed(2)}
                    </div>
                  </td>
                  <td style={{ textAlign: "right" }}>{(item.price * item.quantity).toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="totals space-y-1">
            <div className="flex justify-between">
              <span>Итого</span>
              <span>{sale.total.toFixed(2)} ₸</span>
            </div>
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>Оплачено</span>
              <span>{totalPaid.toFixed(2)} ₸</span>
            </div>
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>Долг</span>
              <span>{sale.credit.toFixed(2)} ₸</span>
            </div>
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>Кассир</span>
              <span>{sale.seller_name || "-"}</span>
            </div>
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>Клиент</span>
              <span>{sale.client_name || "-"}</span>
            </div>
          </div>

          <div className="qr">
            <QRCodeCanvas value={JSON.stringify({ saleId: sale.id, total: sale.total })} size={96} />
            <div className="text-xs text-muted-foreground mt-1">Спасибо за покупку!</div>
          </div>
        </div>
      </Card>
      <Button onClick={handlePrint} className="w-full">
        Печать чека
      </Button>
    </div>
  );
}
