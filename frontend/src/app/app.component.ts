// app.component.ts
import { Component, Inject, OnInit } from '@angular/core';
import { PaymentService } from './payments.service'; // Assuming you have a service to fetch payments
import { TableModule } from 'primeng/table'; 
import { InputTextModule } from 'primeng/inputtext'; 
import { CommonModule } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import { FormsModule } from '@angular/forms';
import { DialogModule } from 'primeng/dialog';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
  imports: [TableModule, CommonModule, InputTextModule, ButtonModule, FormsModule, DialogModule],
  providers: [PaymentService]
})
export class AppComponent implements OnInit {
  payments: any[] = [];
  cols: any[] = [];
  searchQuery: string = '';
  filter: string = '';
  displayDialog: boolean = false;
  selectedPayment: any;

  constructor(@Inject(PaymentService) private paymentService: PaymentService) {}

  ngOnInit() {
    this.paymentService.getPayments().subscribe(data => {
      this.payments = data;
    });

    this.cols = [
      { field: 'payee_first_name', header: 'Payee' },
      { field: 'payee_due_date', header: 'Due Date' },
      { field: 'due_amount', header: 'Due Amount' },
      { field: 'discount_percent', header: 'Discount Percent' },
      { field: 'tax_percent', header: 'Tax Percent' },
      { field: 'total_due', header: 'Total Due' },
      { field: 'payee_payment_status', header: 'Payment Status' },
    ];
  }

  onSearch() {
    // Implement search logic here
  }

  onFilter() {
    // Implement filter logic here
  }

  showPaymentDetails(payment: any) {
    this.selectedPayment = payment;
    this.displayDialog = true;
  }

   editPayment(payment: any) {
    // Implement edit logic here
    console.log('Edit payment:', payment);
  }

  downloadEvidence(paymentId: string) {
    this.paymentService.downloadEvidence(paymentId)
  }
}