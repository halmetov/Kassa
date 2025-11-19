import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

export default function Analysis() {
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [salesByDate, setSalesByDate] = useState<any[]>([]);
  const [topProducts, setTopProducts] = useState<any[]>([]);
  const [salesByPayment, setSalesByPayment] = useState<any[]>([]);
  const [totalStats, setTotalStats] = useState({
    totalSales: 0,
    totalProfit: 0,
    totalDebt: 0,
  });

  useEffect(() => {
    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - 30);
    
    setEndDate(end.toISOString().split('T')[0]);
    setStartDate(start.toISOString().split('T')[0]);
    
    fetchAnalytics(start, end);
  }, []);

  const fetchAnalytics = async (start: Date, end: Date) => {
    // Sales by date
    const { data: sales } = await supabase
      .from('sales')
      .select('*')
      .gte('created_at', start.toISOString())
      .lte('created_at', end.toISOString())
      .order('created_at');

    if (sales) {
      const byDate = sales.reduce((acc: any, sale) => {
        const date = new Date(sale.created_at).toLocaleDateString('ru-RU');
        if (!acc[date]) {
          acc[date] = { date, amount: 0, count: 0 };
        }
        acc[date].amount += parseFloat(sale.total_amount.toString());
        acc[date].count += 1;
        return acc;
      }, {});
      
      setSalesByDate(Object.values(byDate));

      // Total stats
      const totalSales = sales.reduce((sum, s) => sum + parseFloat(s.total_amount.toString()), 0);
      const totalCash = sales.reduce((sum, s) => sum + parseFloat((s.cash_amount || 0).toString()), 0);
      const totalCard = sales.reduce((sum, s) => sum + parseFloat((s.card_amount || 0).toString()), 0);
      const totalDebt = sales.reduce((sum, s) => sum + parseFloat((s.credit_amount || 0).toString()), 0);

      setTotalStats({
        totalSales,
        totalProfit: 0, // Would need purchase prices to calculate
        totalDebt,
      });

      setSalesByPayment([
        { name: 'Наличные', value: totalCash },
        { name: 'Карта', value: totalCard },
        { name: 'В долг', value: totalDebt },
      ]);
    }

    // Top products
    const { data: items } = await supabase
      .from('sale_items')
      .select(`
        *,
        products (name),
        sales!inner (created_at)
      `)
      .gte('sales.created_at', start.toISOString())
      .lte('sales.created_at', end.toISOString());

    if (items) {
      const productStats = items.reduce((acc: any, item) => {
        const productName = item.products?.name || 'Unknown';
        if (!acc[productName]) {
          acc[productName] = { name: productName, quantity: 0, revenue: 0 };
        }
        acc[productName].quantity += parseFloat(item.quantity.toString());
        acc[productName].revenue += parseFloat(item.total.toString());
        return acc;
      }, {});

      const sorted = Object.values(productStats)
        .sort((a: any, b: any) => b.revenue - a.revenue)
        .slice(0, 10);
      
      setTopProducts(sorted);
    }
  };

  const handleFilter = () => {
    if (startDate && endDate) {
      fetchAnalytics(new Date(startDate), new Date(endDate));
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Анализ</h1>
        <p className="text-muted-foreground">Аналитика продаж</p>
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
            <button onClick={handleFilter} className="w-full px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90">
              Применить
            </button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Card className="p-4">
            <div className="text-sm text-muted-foreground">Всего продаж</div>
            <div className="text-3xl font-bold">{totalStats.totalSales.toFixed(2)} ₸</div>
          </Card>
          <Card className="p-4">
            <div className="text-sm text-muted-foreground">Общий долг</div>
            <div className="text-3xl font-bold text-destructive">{totalStats.totalDebt.toFixed(2)} ₸</div>
          </Card>
          <Card className="p-4">
            <div className="text-sm text-muted-foreground">Количество чеков</div>
            <div className="text-3xl font-bold">{salesByDate.reduce((sum, d) => sum + d.count, 0)}</div>
          </Card>
        </div>

        {/* Sales by Date Chart */}
        <Card className="p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">Продажи по дням</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={salesByDate}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="amount" stroke="#8884d8" name="Сумма (₸)" />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Top Products Chart */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Топ 10 товаров</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={topProducts}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="revenue" fill="#8884d8" name="Выручка (₸)" />
              </BarChart>
            </ResponsiveContainer>
          </Card>

          {/* Payment Methods Pie Chart */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Способы оплаты</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={salesByPayment}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}: ${entry.value.toFixed(0)} ₸`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {salesByPayment.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </div>
      </Card>
    </div>
  );
}
