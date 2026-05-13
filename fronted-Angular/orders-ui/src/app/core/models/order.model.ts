export type OrderStatus = 'PENDING' | 'CONFIRMED' | 'SHIPPED' | 'DELIVERED';

export interface Order {
  id: number;
  customerName: string;
  items: string[];
  total: number;
  status: OrderStatus;
}