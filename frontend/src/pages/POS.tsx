import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { toast } from "sonner";
import { Search, ShoppingCart, Trash2, Plus, Minus } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { getCurrentUser, getEmployeeByUserId } from "@/lib/auth";

type CartItem = {
  product_id: string;
  name: string;
  price: number;
  quantity: number;
  total: number;
};

export default function POS() {
  const [categories, setCategories] = useState<any[]>([]);
  const [products, setProducts] = useState<any[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<any[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [cart, setCart] = useState<CartItem[]>([]);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [branches, setBranches] = useState<any[]>([]);
  const [clients, setClients] = useState<any[]>([]);
  const [selectedBranch, setSelectedBranch] = useState("");
  const [cashAmount, setCashAmount] = useState("");
  const [cardAmount, setCardAmount] = useState("");
  const [creditAmount, setCreditAmount] = useState("");
  const [selectedClient, setSelectedClient] = useState("");
  const [employee, setEmployee] = useState<any>(null);

  useEffect(() => {
    fetchData();
    loadEmployee();
  }, []);

  useEffect(() => {
    filterProducts();
  }, [selectedCategory, searchQuery, products]);

  const loadEmployee = async () => {
    const user = await getCurrentUser();
    if (user) {
      const emp = await getEmployeeByUserId(user.id);
      setEmployee(emp);
      if (emp?.branch_id) {
        setSelectedBranch(emp.branch_id);
      }
    }
  };

  const fetchData = async () => {
    const [categoriesRes, productsRes, branchesRes, clientsRes] = await Promise.all([
      supabase.from('categories').select('*').order('name'),
      supabase.from('products').select('*').order('name'),
      supabase.from('branches').select('*').eq('is_active', true).order('name'),
      supabase.from('clients').select('*').order('name'),
    ]);

    if (categoriesRes.data) setCategories(categoriesRes.data);
    if (productsRes.data) setProducts(productsRes.data);
    if (branchesRes.data) setBranches(branchesRes.data);
    if (clientsRes.data) setClients(clientsRes.data);
  };

  const filterProducts = () => {
    let filtered = products;

    if (selectedCategory) {
      filtered = filtered.filter(p => p.category_id === selectedCategory);
    }

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        p => p.name.toLowerCase().includes(query) || 
             p.barcode?.toLowerCase().includes(query)
      );
    }

    setFilteredProducts(filtered);
  };

  const addToCart = (product: any) => {
    const existingItem = cart.find(item => item.product_id === product.id);
    
    if (existingItem) {
      setCart(cart.map(item =>
        item.product_id === product.id
          ? { ...item, quantity: item.quantity + 1, total: (item.quantity + 1) * item.price }
          : item
      ));
    } else {
      setCart([...cart, {
        product_id: product.id,
        name: product.name,
        price: product.sale_price,
        quantity: 1,
        total: product.sale_price,
      }]);
    }
  };

  const updateQuantity = (product_id: string, delta: number) => {
    setCart(cart.map(item => {
      if (item.product_id === product_id) {
        const newQty = Math.max(1, item.quantity + delta);
        return { ...item, quantity: newQty, total: newQty * item.price };
      }
      return item;
    }));
  };

  const updatePrice = (product_id: string, newPrice: number) => {
    setCart(cart.map(item =>
      item.product_id === product_id
        ? { ...item, price: newPrice, total: item.quantity * newPrice }
        : item
    ));
  };

  const removeFromCart = (product_id: string) => {
    setCart(cart.filter(item => item.product_id !== product_id));
  };

  const getTotalAmount = () => {
    return cart.reduce((sum, item) => sum + item.total, 0);
  };

  const handlePayment = async () => {
    if (!selectedBranch) {
      toast.error("Выберите филиал");
      return;
    }

    if (cart.length === 0) {
      toast.error("Корзина пуста");
      return;
    }

    const totalAmount = getTotalAmount();
    const cash = parseFloat(cashAmount) || 0;
    const card = parseFloat(cardAmount) || 0;
    const credit = parseFloat(creditAmount) || 0;
    const paidTotal = cash + card + credit;

    if (paidTotal !== totalAmount) {
      toast.error("Сумма оплаты не совпадает с итогом");
      return;
    }

    if (credit > 0 && !selectedClient) {
      toast.error("Выберите клиента для кредита");
      return;
    }

    try {
      const { data: saleData, error: saleError } = await supabase
        .from('sales')
        .insert({
          total_amount: totalAmount,
          cash_amount: cash,
          card_amount: card,
          credit_amount: credit,
          branch_id: selectedBranch,
          employee_id: employee?.id,
          client_id: selectedClient || null,
        })
        .select()
        .single();

      if (saleError) throw saleError;

      const { error: itemsError } = await supabase
        .from('sale_items')
        .insert(
          cart.map(item => ({
            sale_id: saleData.id,
            product_id: item.product_id,
            quantity: item.quantity,
            price: item.price,
            total: item.total,
          }))
        );

      if (itemsError) throw itemsError;

      if (credit > 0 && selectedClient) {
        const client = clients.find(c => c.id === selectedClient);
        await supabase
          .from('clients')
          .update({ debt: (client.debt || 0) + credit })
          .eq('id', selectedClient);
      }

      toast.success("Продажа завершена успешно");
      setCart([]);
      setShowPaymentModal(false);
      setCashAmount("");
      setCardAmount("");
      setCreditAmount("");
      setSelectedClient("");
    } catch (error: any) {
      toast.error("Ошибка при оформлении продажи");
      console.error(error);
    }
  };

  return (
    <div className="h-full flex flex-col lg:flex-row gap-4">
      <div className="flex-1 space-y-4">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Поиск по названию или штрихкоду..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        <div className="flex gap-2 overflow-x-auto pb-2">
          <Button
            variant={!selectedCategory ? "default" : "outline"}
            size="sm"
            onClick={() => setSelectedCategory(null)}
          >
            Все
          </Button>
          {categories.map(cat => (
            <Button
              key={cat.id}
              variant={selectedCategory === cat.id ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedCategory(cat.id)}
            >
              {cat.name}
            </Button>
          ))}
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {filteredProducts.map(product => (
            <Card
              key={product.id}
              className="p-4 cursor-pointer hover:shadow-lg transition-shadow"
              onClick={() => addToCart(product)}
            >
              <div className="space-y-2">
                <div className="font-medium line-clamp-2">{product.name}</div>
                <div className="text-lg font-bold text-primary">
                  {product.sale_price} ₸
                </div>
                <div className="text-sm text-muted-foreground">
                  Остаток: {product.quantity || 0} {product.unit}
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      <Card className="w-full lg:w-96 p-4 flex flex-col">
        <div className="flex items-center gap-2 mb-4">
          <ShoppingCart className="h-5 w-5" />
          <h2 className="text-xl font-bold">Корзина</h2>
        </div>

        <div className="flex-1 space-y-2 overflow-auto mb-4">
          {cart.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              Корзина пуста
            </div>
          ) : (
            cart.map(item => (
              <Card key={item.product_id} className="p-3">
                <div className="space-y-2">
                  <div className="flex justify-between items-start">
                    <div className="font-medium flex-1">{item.name}</div>
                    <Button
                      size="icon"
                      variant="ghost"
                      onClick={() => removeFromCart(item.product_id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Button
                      size="icon"
                      variant="outline"
                      onClick={() => updateQuantity(item.product_id, -1)}
                    >
                      <Minus className="h-4 w-4" />
                    </Button>
                    <Input
                      type="number"
                      value={item.quantity}
                      onChange={(e) => {
                        const val = parseInt(e.target.value) || 1;
                        updateQuantity(item.product_id, val - item.quantity);
                      }}
                      className="w-16 text-center"
                    />
                    <Button
                      size="icon"
                      variant="outline"
                      onClick={() => updateQuantity(item.product_id, 1)}
                    >
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>

                  <div className="flex gap-2">
                    <Input
                      type="number"
                      value={item.price}
                      onChange={(e) => updatePrice(item.product_id, parseFloat(e.target.value) || 0)}
                      className="flex-1"
                    />
                    <div className="font-bold text-lg">
                      {item.total.toFixed(2)} ₸
                    </div>
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>

        <div className="space-y-4 border-t pt-4">
          <div className="flex justify-between text-2xl font-bold">
            <span>Итого:</span>
            <span>{getTotalAmount().toFixed(2)} ₸</span>
          </div>

          <Button
            className="w-full"
            size="lg"
            onClick={() => setShowPaymentModal(true)}
            disabled={cart.length === 0}
          >
            Оплата
          </Button>
        </div>
      </Card>

      <Dialog open={showPaymentModal} onOpenChange={setShowPaymentModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Оплата</DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <Label>Филиал</Label>
              <Select value={selectedBranch} onValueChange={setSelectedBranch}>
                <SelectTrigger>
                  <SelectValue placeholder="Выберите филиал" />
                </SelectTrigger>
                <SelectContent>
                  {branches.map(branch => (
                    <SelectItem key={branch.id} value={branch.id}>
                      {branch.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>Наличные</Label>
              <Input
                type="number"
                value={cashAmount}
                onChange={(e) => setCashAmount(e.target.value)}
                placeholder="0"
              />
            </div>

            <div>
              <Label>Карта</Label>
              <Input
                type="number"
                value={cardAmount}
                onChange={(e) => setCardAmount(e.target.value)}
                placeholder="0"
              />
            </div>

            <div>
              <Label>В долг</Label>
              <Input
                type="number"
                value={creditAmount}
                onChange={(e) => setCreditAmount(e.target.value)}
                placeholder="0"
              />
            </div>

            {parseFloat(creditAmount) > 0 && (
              <div>
                <Label>Клиент</Label>
                <Select value={selectedClient} onValueChange={setSelectedClient}>
                  <SelectTrigger>
                    <SelectValue placeholder="Выберите клиента" />
                  </SelectTrigger>
                  <SelectContent>
                    {clients.map(client => (
                      <SelectItem key={client.id} value={client.id}>
                        {client.name} {client.phone && `(${client.phone})`}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            <div className="flex justify-between text-xl font-bold pt-4 border-t">
              <span>Итого:</span>
              <span>{getTotalAmount().toFixed(2)} ₸</span>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowPaymentModal(false)}>
              Отмена
            </Button>
            <Button onClick={handlePayment}>Подтвердить</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
