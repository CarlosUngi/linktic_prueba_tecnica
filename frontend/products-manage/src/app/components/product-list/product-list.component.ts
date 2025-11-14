import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms'; // Importar FormsModule
import { catchError, tap } from 'rxjs/operators';
import { of } from 'rxjs';
import { ProductWithStock } from '../../../models/product.model';
import { InventoryService } from '../../../services/inventory.service';

// Tipo extendido para incluir la cantidad de compra en el frontend
type ProductForCart = ProductWithStock & { purchaseQuantity: number | null };

@Component({
  selector: 'app-product-list',
  standalone: true,
  imports: [CommonModule, FormsModule], // Añadir FormsModule
  templateUrl: './product-list.component.html',
  styleUrl: './product-list.component.css'
})
export class ProductListComponent implements OnInit {

  products: ProductForCart[] = [];
  isLoading = true;
  errorMessage: string | null = null;

  constructor(
    private inventoryService: InventoryService
  ) {}

  ngOnInit(): void {
    this.loadProducts();
  }

  loadProducts(): void {
    this.isLoading = true;
    this.errorMessage = null;
    this.inventoryService.getProductsWithStock(1, 10).pipe(
      catchError(err => {
        console.error('Error loading products:', err);
        this.errorMessage = 'No se pudieron cargar los productos. Verifique que los servicios de backend estén en ejecución.';
        this.isLoading = false;
        return of({ data: [], meta: {} });
      })
    ).subscribe(response => {
      // Mapear la respuesta para añadir la propiedad 'purchaseQuantity'
      this.products = response.data.map(p => ({ ...p, purchaseQuantity: null }));
      this.isLoading = false;
    });
  }

  purchase(product: ProductForCart): void {
    if (!product.purchaseQuantity || product.purchaseQuantity <= 0) {
      this.errorMessage = 'Por favor, ingrese una cantidad válida.';
      return;
    }

    if (product.purchaseQuantity > product.attributes.available_stock) {
      this.errorMessage = 'No puede comprar más de la cantidad disponible en stock.';
      return;
    }

    this.errorMessage = null;
    const productId = product.attributes.id;
    const quantity = product.purchaseQuantity;

    this.inventoryService.purchaseProduct(productId, quantity).pipe(
      tap(() => {
        // Evento en consola como solicitó el usuario
        console.log(`%cCompra exitosa!`, 'color: green; font-weight: bold;', {
          producto: product.attributes.name,
          cantidad: quantity,
          id: productId,
          timestamp: new Date().toISOString()
        });
      }),
      catchError(err => {
        console.error('Error during purchase:', err);
        this.errorMessage = err.error?.message || 'Ocurrió un error durante la compra. Intente de nuevo.';
        return of(null); // No continuar el pipe
      })
    ).subscribe(result => {
      // Si la compra fue exitosa (result no es null)
      if (result) {
        this.loadProducts(); // Recargar productos para actualizar el stock
      }
    });
  }
}