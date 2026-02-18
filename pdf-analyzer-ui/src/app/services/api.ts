import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export type Analysis = {
  titre: string;
  resume: string;
  mots_cles: string[];
  type_document: 'facture' | 'contrat' | 'article' | 'rapport' | 'cv' | 'autre';
  langue: 'fr' | 'en' | 'autre';
};
export type ProcessResponse = {
  filename: string;
  chars: number;
  ocr_used: boolean;
  analysis: Analysis;
};


@Injectable({
  providedIn: 'root',
})
export class Api {
   private baseUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  processPdf(file: File): Observable<ProcessResponse> {
    const form = new FormData();
    form.append('file', file, file.name);
    return this.http.post<ProcessResponse>(`${this.baseUrl}/process`, form);
  }
}
