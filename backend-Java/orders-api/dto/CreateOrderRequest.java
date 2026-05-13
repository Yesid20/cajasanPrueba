package com.example.orders.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;

import java.util.List;

public class CreateOrderRequest {

    @NotBlank(message = "customerName es obligatorio")
    private String customerName;

    @NotEmpty(message = "items no puede estar vacío")
    private List<@NotBlank(message = "Cada item debe tener texto") String> items;

    @Min(value = 1, message = "total debe ser mayor que 0")
    private Integer total;

    public CreateOrderRequest() {
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
}