import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';

import { OrderService } from '../../core/services/order.service';
import { Order, OrderStatus } from '../../core/models/order.model';

@Component({
  selector: 'app-order-detail',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule],
  templateUrl: './order-detail.component.html',
  styleUrls: ['./order-detail.component.css']
})
export class OrderDetailComponent implements OnInit {

  order: Order | null = null;
  loading = false;
  error: string | null = null;

  selectedStatus: OrderStatus = 'PENDING';
  updating = false;

  constructor(
    private route: ActivatedRoute,
    private orderService: OrderService
  ) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.loadOrder(id);
  }

  loadOrder(id: number) {
    this.loading = true;
    this.error = null;

    this.orderService.getOrderById(id).subscribe({
      next: (data) => {
        this.order = data;
        this.selectedStatus = data.status;
        this.loading = false;
      },
      error: () => {
        this.error = 'No se pudo cargar la orden.';
        this.loading = false;
      }
    });
  }

  updateStatus() {
    if (!this.order) return;

    this.updating = true;
    this.error = null;

    this.orderService.updateOrderStatus(this.order.id, this.selectedStatus).subscribe({
      next: (updated) => {
        this.order = updated;
        this.updating = false;
      },
      error: () => {
        this.error = 'Error actualizando el estado.';
        this.updating = false;
      }
    });
  }

  getStatusClass(status: string): string {
    switch (status) {
      case 'PENDING': return 'badge pending';
      case 'CONFIRMED': return 'badge confirmed';
      case 'SHIPPED': return 'badge shipped';
      case 'DELIVERED': return 'badge delivered';
      default: return 'badge';
    }
  }
}