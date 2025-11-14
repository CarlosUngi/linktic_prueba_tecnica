import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { catchError } from 'rxjs/operators';
import { of } from 'rxjs';
import { CreateProductDTO, ProductAttributes, ProductWithStock, UpdateProductDTO } from '../../../models/product.model';
import { ProductFormComponent } from '../../product-form.component';
import { InventoryService } from '../../../services/inventory.service';
import { ProductsService } from '../../../services/products.service';

@Component({
  selector: 'app-product-list',
  standalone: true,
  imports: [CommonModule, ProductFormComponent],
  templateUrl: './product-list.component.html',
  styleUrl: './product-list.component.css'
})
export class ProductListComponent implements OnInit {

  products: ProductWithStock[] = [];
  selectedProduct: ProductAttributes | null = null;
  isLoading = true;
  isFormVisible = false;
  errorMessage: string | null = null;

  constructor(
    private inventoryService: InventoryService,
    private productsService: ProductsService
  ) {}

  ngOnInit(): void {
    this.loadProducts();
  }

  loadProducts(): void {
    this.isLoading = true;
    this.errorMessage = null;
    this.inventoryService.getProductsWithStock(1, 10).pipe(
      catchError(err => {
        this.errorMessage = 'No se pudieron cargar los productos. Verifique que los servicios de backend estén en ejecución.';
        this.isLoading = false;
        return of({ data: [], meta: {} });
      })
    ).subscribe(response => {
      this.products = response.data;
      this.isLoading = false;
    });
  }

  openCreateForm(): void {
    this.selectedProduct = null;
    this.isFormVisible = true;
  }

  openEditForm(product: ProductWithStock): void {
    this.selectedProduct = product.attributes;
    this.isFormVisible = true;
  }

  closeForm(): void {
    this.isFormVisible = false;
    this.selectedProduct = null;
  }

  saveProduct(productData: CreateProductDTO | UpdateProductDTO): void {
    const operation = this.selectedProduct
      ? this.productsService.updateProduct(this.selectedProduct.id, productData)
      : this.productsService.createProduct(productData as CreateProductDTO);

    operation.subscribe(() => {
      this.closeForm();
      this.loadProducts();
    });
  }

  deleteProduct(id: number): void {
    if (confirm('¿Está seguro de que desea eliminar este producto?')) {
      this.productsService.deleteProduct(id).subscribe(() => {
        this.loadProducts();
      });
    }
  }
}