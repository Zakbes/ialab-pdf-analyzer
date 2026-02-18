import { Component, ChangeDetectorRef, NgZone , ApplicationRef} from '@angular/core';
import { CommonModule } from '@angular/common';
import { Api, ProcessResponse } from '../services/api';

@Component({
  selector: 'app-analyzer',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './analyzer.html',
  styleUrls: ['./analyzer.css'],
})
export class AnalyzerComponent {
  selectedFile: File | null = null;
  isDragOver = false;

  loading = false;
  result: ProcessResponse | null = null;
  errorMsg: string | null = null;

  constructor(
    private api: Api,
    private zone: NgZone,
    private cdr: ChangeDetectorRef,
    private appRef: ApplicationRef
  ) {}

  openFileBrowser(event: MouseEvent, fileInput: HTMLInputElement) {
    event.preventDefault();
    fileInput.click();
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0] ?? null;
    this.handleFile(file);
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
    this.isDragOver = true;
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
    this.isDragOver = false;
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    this.isDragOver = false;
    const file = event.dataTransfer?.files?.[0] ?? null;
    this.handleFile(file);
  }

  handleFile(file: File | null) {
    this.errorMsg = null;
    this.result = null;

    if (!file) return;

    if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
      this.errorMsg = 'Merci de sélectionner un fichier PDF.';
      return;
    }

    this.selectedFile = file;
    // refresh immédiat
    this.cdr.detectChanges();
  }

  reset() {
    this.selectedFile = null;
    this.result = null;
    this.errorMsg = null;
    this.loading = false;

    this.cdr.detectChanges();
  }

  process() {
    if (!this.selectedFile) return;

    this.loading = true;
    this.errorMsg = null;
    this.result = null;

    // refresh immédiat avant appel
    this.cdr.detectChanges();

    this.api.processPdf(this.selectedFile).subscribe({
      next: (res) => {
        console.log('PROCESS OK:', res);

        // Forcer Angular à prendre en compte la mise à jour
        this.zone.run(() => {
          this.result = res;
          this.loading = false;
          this.errorMsg = null;
          this.cdr.detectChanges();
          this.appRef.tick();
        });
      },
      error: (err) => {
        console.error('PROCESS ERROR:', err);

        this.zone.run(() => {
          this.loading = false;
          this.result = null;
          this.errorMsg = err?.error?.detail || 'Erreur lors du traitement.';
          this.cdr.detectChanges();
        });
      },
    });
  }
}
