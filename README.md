# Capstone Project 3

Repositori ini adalah hasil kerja saya untuk tugas Capstone Project ke-3 untuk Kelas Data Engineering Purwadhika. Secara garis besar saya diminta untuk membuat suatu pipeline yang mengutilisasi Airflow sebagai *orchestrator* dua DAG (Directed Acyiclic Graph) yang bertujuan untuk (1) Generasi *dummy data* dan menyimpannya dalam suatu database (PostgreSQL) dan (2) melakukan ingestion data tersebut dari database ke Google BigQuery, suatu cloud-based data warehouse. Graph dibawah dapat dilihat sebagai gambaran umum project ini.

<img src='assets/project_graph.png' alt='project graph' width='50%'>

Seperti yang bisa kita lihat di gambar diatas, untuk seluruh local service yang kita bangun (Airflow & PostgreSQL) dijalankan melalui Docker. Docker sangat membantu, karena tools tersebut memudahkan kita untuk melakukan instalasi terhadap service-service tersebut sebagaimana virtual computer namun dilakukan dalam komputer lokal kita. 

## Cara Menggunakan

Sebelum menjalankan program ini, Kita harus memastikan bahwa network yang digunakan antar container untuk berkomunikasi dengan satu sama lain sudah berjalan. Untuk itu kita bisa meng-check terlebih dahulu dan menjalankan perintah dibawah dalam terminal.

```
$ docker network ls
```

lalu jika memang network yang digunakan belum berjalan kita bisa menjalankannya dengan (dalam project ini menggunakan network `application-network`)

```
$ docker network create application-network
```

Dengan menggunakan network, ini dapat memudahkan komunikasi antar container dimana kita menggunakan nama service kita sebagai *host* dan menggunakan container port yang kita tuliskan didalam file `docker-compose.yaml` kita. Hal ini juga meningkatkan security, membantu kita untuk mengawasi dan mengatur external access dengan lebih mudah.

Lalu setelah memastikan network kita sudah berjalan, menjalankan docker container kita dalam ketiga directory container kita yaitu `app_db`, `prod_airflow_db,` dan `prod_airflow_service`. Jangan lupa juga untuk mematikan proccess dalam port `5432` karena container PostgreSQL kita menggunakan port tersebut sebagai `host_port`.

```
$ docker compose up -d
```

Setelah itu kita bisa membuka webserver airflow di browser dengan membuka `localhost:8080/`. Di dalam web UI tersebut, karena project kita didesain untuk dijalankan setiap satu jam, kita hanya perlu mengeser tombol yang berada disebelah DAG kita.