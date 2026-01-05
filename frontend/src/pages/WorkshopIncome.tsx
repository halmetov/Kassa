import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function WorkshopIncome() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Приход (Цех)</CardTitle>
      </CardHeader>
      <CardContent>
        Функционал прихода в цех доступен через backend endpoint /api/workshop/products для выбора остатков. Добавление прихода требует доработки учета товаров.
      </CardContent>
    </Card>
  );
}
