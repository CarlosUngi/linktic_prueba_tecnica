import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ProductAttributes } from '../models/product.model';

@Component({
  selector: 'app-product-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './product-form.component.html',
  styleUrl: './product-form.component.css'
})
export class ProductFormComponent implements OnChanges {
  @Input() product: ProductAttributes | null = null;
  @Input() isVisible = false;
  @Output() save = new EventEmitter<any>();
  @Output() close = new EventEmitter<void>();

  productForm: FormGroup;
  isEditMode = false;

  constructor(private fb: FormBuilder) {
    this.productForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(3)]],
      description: [''],
      price: [0, [Validators.required, Validators.min(0.01)]]
    });
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['product'] && this.product) {
      this.isEditMode = true;
      this.productForm.patchValue({
        name: this.product.name,
        description: this.product.description,
        price: this.product.price
      });
    } else if (!this.product) {
      this.isEditMode = false;
      this.productForm.reset({ name: '', description: '', price: 0 });
    }
  }

  onSave(): void {
    if (this.productForm.valid) {
      this.save.emit(this.productForm.value);
    }
  }

  onClose(): void {
    this.close.emit();
  }

  get name() { return this.productForm.get('name'); }
  get price() { return this.productForm.get('price'); }
}