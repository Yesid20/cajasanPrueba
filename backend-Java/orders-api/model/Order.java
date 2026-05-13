package com.example.orders.model;

import java.util.List;

public class Order {

    private Long id;
    private String customerName;
    private List<String> items;
    private Integer total;
    private OrderStatus status;

    public Order() {
    }

    public Order(Long id, String customerName, List<String> items, Integer total, OrderStatus status) {
        this.id = id;
        this.customerName = customerName;
        this.items = items;
        this.total = total;
        this.status = status;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getCustomerName() {
        return customerName;
    }

    public void setCustomerName(String customerName) {
        this.customerName = customerName;
    }

    public List<String> getItems() {
        return items;
    }

    public void setItems(List<String> items) {
        this.items = items;
    }

    public Integer getTotal() {
        return total;
    }

    public void setTotal(Integer total) {
        this.total = total;
    }

    public OrderStatus getStatus() {
        return status;
    }

    public void setStatus(OrderStatus status) {
        this.status = status;
    }
}