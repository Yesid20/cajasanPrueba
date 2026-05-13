package com.example.orders.service;

import com.example.orders.dto.CreateOrderRequest;
import com.example.orders.dto.UpdateOrderStatusRequest;
import com.example.orders.exception.NotFoundException;
import com.example.orders.model.Order;
import com.example.orders.model.OrderStatus;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicLong;

@Service
public class OrderService {

    private final List<Order> orders = new ArrayList<>();
    private final AtomicLong idGenerator = new AtomicLong(1);

    public OrderService() {
        orders.add(new Order(
                idGenerator.getAndIncrement(),
                "Juan Pérez",
                List.of("Camiseta", "Zapatos"),
                149900,
                OrderStatus.PENDING
        ));

        orders.add(new Order(
                idGenerator.getAndIncrement(),
                "María Gómez",
                List.of("Bolso", "Lentes"),
                220000,
                OrderStatus.CONFIRMED
        ));

        orders.add(new Order(
                idGenerator.getAndIncrement(),
                "Carlos Ruiz",
                List.of("Pantalón"),
                85000,
                OrderStatus.SHIPPED
        ));
    }

    public List<Order> findAll() {
        return orders;
    }

    public Order findById(Long id) {
        return orders.stream()
                .filter(order -> order.getId().equals(id))
                .findFirst()
                .orElseThrow(() -> new NotFoundException("Order with id " + id + " not found"));
    }

    public Order create(CreateOrderRequest request) {
        Order order = new Order(
                idGenerator.getAndIncrement(),
                request.getCustomerName(),
                request.getItems(),
                request.getTotal(),
                OrderStatus.PENDING
        );

        orders.add(order);
        return order;
    }

    public Order updateStatus(Long id, UpdateOrderStatusRequest request) {
        Order order = findById(id);
        order.setStatus(request.getStatus());
        return order;
    }
}