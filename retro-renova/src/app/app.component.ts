import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HttpClientModule } from '@angular/common/http';

// Defina uma interface para a resposta esperada.
interface ImageResponse {
  processedImageUrl: string;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [HttpClientModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'], // Corrija de 'styleUrl' para 'styleUrls'
})
export class AppComponent {
  title = 'retro-renova';
  processedImageUrl: string = 'assets/images/default-image.png';

  constructor(private http: HttpClient) {}

  adicionarItem() {
    console.log('item adicionado!');
  }

  onFileSelected(event: any): void {
    const file: File = event.target.files[0];

    if (file) {
      const formData = new FormData();
      formData.append('image', file);

      this.http
        .post<ImageResponse>('http://localhost:5000/process-image', formData)
        .subscribe({
          next: (response) => {
            // Atualize a URL da imagem processada.
            console.log(response.processedImageUrl);
            this.processedImageUrl = `http://localhost:5000${response.processedImageUrl}?${new Date().getTime()}`;
          },
          error: (error) => {
            console.error('Erro ao processar a imagem:', error);
          },
        });
    }
  }
}
