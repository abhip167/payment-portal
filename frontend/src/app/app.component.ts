// app.component.ts
import { Component, Inject, OnDestroy, OnInit } from '@angular/core';
import { PaymentService } from './payments.service'; // Assuming you have a service to fetch payments
import { TableModule } from 'primeng/table';
import { InputTextModule } from 'primeng/inputtext';
import { CommonModule } from '@angular/common';
import { ButtonModule } from 'primeng/button';
import { AbstractControl, FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { DialogModule } from 'primeng/dialog';
import { DropdownModule } from 'primeng/dropdown';
import { DatePickerModule } from 'primeng/datepicker';
import { FileUploadModule } from 'primeng/fileupload';



import { SubSink } from 'subsink';
import { CheckboxModule } from 'primeng/checkbox';
import { InputNumberModule } from 'primeng/inputnumber';
import { of, switchMap } from 'rxjs';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
  imports: [TableModule, CommonModule, 
    InputTextModule,
    ButtonModule, FormsModule, DialogModule, ReactiveFormsModule, 
    DropdownModule, DatePickerModule,
  CheckboxModule, InputNumberModule, FileUploadModule],
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
    { label: 'Pending', value: 'pending', inactive: false },
    { label: 'Due Now', value: 'due_now', inactive: false },
    { label: 'Over Due', value: 'overdue', inactive: true },
    { label: 'Completed', value: 'completed', inactive: false }
  ];

  private subs = new SubSink();

  get isPaymentStatusCompleted() {
    return this.editForm?.get('payee_payment_status')?.value === 'completed';
  }

  get evidenceUploadUrl() {
    return `${this.paymentService.paymentsUrl}/${this.selectedPayment.id}/evidence`;
  }

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
      payee_due_date: [new Date(), Validators.required],
      due_amount: ['', Validators.required],
      payee_payment_status: [false, Validators.required],
      evidence_file_id: [null],
      evidence_file: [null]
    }, { validator: this.evidenceFileValidator });
  }

  
  ngOnInit() {
    this.subs.sink = this.paymentService.getPayments().subscribe(data => {
      this.payments = data;
    });
  }

  evidenceFileValidator(control: AbstractControl): { [key: string]: boolean } | null {
    const status = control.get('payee_payment_status')?.value;
    const evidenceFile = control.get('evidence_file')?.value;
    if (status === 'completed' && !evidenceFile) {
      return { 'evidenceFileRequired': true };
    }
    return null;
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
      payee_due_date: new Date(payment.payee_due_date),
      due_amount: payment.due_amount,
      payee_payment_status: payment.payee_payment_status,
    });
    this.editDialog = true;
  }

  editPayment() {
    if (this.editForm.valid) {
      const formValues = this.editForm.value;
  
      const uploadEvidence$ = formValues.evidence_file
        ? this.paymentService.uploadEvidence(this.selectedPayment.id, formValues.evidence_file).pipe(
            switchMap(data => {
              if (data?.evidence_file_id) {
                this.editForm.patchValue({ evidence_file_id: data.evidence_file_id });
              }
              console.log('Uploaded evidence:', data);
              return of(data);
            })
          )
        : of(null);
  
      this.subs.sink = uploadEvidence$.pipe(
        switchMap((data) => {
          const editFormValues = this.editForm.value;

          const updatedPayment = {
            payee_due_date: editFormValues.payee_due_date,
            due_amount: editFormValues.due_amount,
            payee_payment_status: editFormValues.payee_payment_status,
            evidence_file_id: editFormValues.evidence_file_id
          }
  
          return this.paymentService.editPayment(this.selectedPayment.id, updatedPayment);
        })
      ).subscribe(data => {
        console.log('Updated payment:', data);
        this.editDialog = false;
        this.selectedPayment = null;
      });
    }
  }
  downloadEvidence(paymentId: string) {
    this.paymentService.downloadEvidence(paymentId)
  }

  onFileChange(event: any) {
    const file = event.target.files[0];
    if (file) {
      this.editForm.patchValue({ evidence_file: file });
    }
  }

  ngOnDestroy() {
    this.subs.unsubscribe();
  }
}