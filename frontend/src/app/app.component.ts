// app.component.ts
import { Component, Inject, OnDestroy, OnInit } from '@angular/core';
import { PaymentService } from './payments.service'; // Assuming you have a service to fetch payments
import { TableModule } from 'primeng/table';
import { InputTextModule } from 'primeng/inputtext';
import { CommonModule } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { DialogModule } from 'primeng/dialog';
import { DropdownModule } from 'primeng/dropdown';
import { DatePickerModule } from 'primeng/datepicker';


import { SubSink } from 'subsink';
import { CheckboxModule } from 'primeng/checkbox';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
  imports: [TableModule, CommonModule, 
    InputTextModule,
    ButtonModule, FormsModule, DialogModule, ReactiveFormsModule, 
    DropdownModule, DatePickerModule,
  CheckboxModule],
  providers: [PaymentService]
})
export class AppComponent implements OnInit, OnDestroy {
  payments: any[] = [];
  cols: any[] = [];
  searchQuery: string = '';
  filter: string = '';
  displayDialog: boolean = false;
  editDialog: boolean = false;
  selectedPayment: any;
  editForm: FormGroup;
  statuses: any[] = [
    { label: 'Pending', value: 'pending' },
    { label: 'Due Now', value: 'due_now' },
    { label: 'Completed', value: 'completed' }
  ];

  private subs = new SubSink();


  constructor(@Inject(PaymentService) private paymentService: PaymentService,
    private fb: FormBuilder
  ) {
    this.cols = [
      { field: 'payee_first_name', header: 'Payee' },
      { field: 'payee_due_date', header: 'Due Date' },
      { field: 'due_amount', header: 'Due Amount' },
      { field: 'discount_percent', header: 'Discount Percent' },
      { field: 'tax_percent', header: 'Tax Percent' },
      { field: 'total_due', header: 'Total Due' },
      { field: 'payee_payment_status', header: 'Payment Status' },
    ];

    this.editForm = this.fb.group({
      payee_due_date: ['', Validators.required],
      due_amount: ['', Validators.required],
      payee_payment_status: ['', Validators.required],
      evidence_file: [Blob, Validators.required]
    });
  }

  ngOnInit() {
    this.subs.sink = this.paymentService.getPayments().subscribe(data => {
      this.payments = data;
    });


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

  openEditPaymentDialog(payment: any) {
    this.selectedPayment = payment;
    this.editForm.patchValue({
      payee_due_date: payment.payee_due_date,
      due_amount: payment.due_amount,
      payee_payment_status: payment.payee_payment_status
    });
    this.editDialog = true;
  }

  editPayment() {
    if (this.editForm.valid) {
      const updatedPayment: { [key: string]: any } = {};
      Object.keys(this.editForm.controls).forEach(key => {
        if (this.editForm.controls[key].dirty) {
          updatedPayment[key] = this.editForm.controls[key].value;
        }
      });

      this.subs.sink = this.paymentService.editPayment(this.selectedPayment.id, updatedPayment).subscribe(data => {
        this.payments = data;
      });
      console.log('Updated payment:', updatedPayment);
      this.editDialog = false;
      this.selectedPayment = null;
    }
  }

  downloadEvidence(paymentId: string) {
    this.paymentService.downloadEvidence(paymentId)
  }

  onFileChange(event: any) {
    const file = event.target.files[0];
    if (file) {
      this.selectedPayment.evidence_file_id = file; // Update the evidence file ID
    }
  }

  ngOnDestroy() {
    this.subs.unsubscribe();
  }
}