import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function WorkshopExpenses() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Производственные расходы</CardTitle>
      </CardHeader>
      <CardContent>
        Управление расходами цеха может быть добавлено отдельно. Пока доступен базовый отчет закрытых заказов.
      </CardContent>
    </Card>
  );
}
