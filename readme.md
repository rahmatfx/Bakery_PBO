
# Game Cozy Bakery Berbasis Pygame

Game Cozy Bakery yang kami buat adalah sebuah game berbasis bahasa pemrograman Python yang dirancang dan dibangun sepenuh nya menggunakan library PyGame. Di dalam game ini player bermain sebagai seorang pemilik bakery yang bertugas melayani pelanggan yang datang, berbincang dengan mereka dan membuatkan kue yang sesuai dengan preferensi tiap pelanggan. Main gameplay loop dimulai dari berbincang dengan para pelanggan, memilih opsi dialog yang ada dan memilih pilihan kue yang sekiranya sesuai dengan sifat dan karakteristik tiap pelanggan, player lalu berpindah ruangan dan mulai membuat kue, memilih hal seperti adonan dan cetakan yang sesuai, memanggang adonan menjadi roti lalu memilih dekorasi yang sesuai, semua dalam rentan waktu.


## Anggota Kelompok

- Ravelino Hermanto (25051204151)
- Mark Jhonson Prasetia (25051204154)
- Rahmat Arif Anwar (25051204156) 
- Ardra Revanda Rafif Akbar (25051204204)


## Fitur Utama

Fitur utama dari game ini adalah interaksi dari setiap ruangan di dalam game yang menawarkan simulasi menjadi seorang bakery. Mulai dari ruangan kasir yang mengharuskan player untuk berinteraksi dengan pelanggan dan menerima pesanan. Kemudian ruangan dough untuk player membuat adonan dan mencetak adonan tersebut sesuai pesanan pelanggan. Kemudian, terdapat ruangan Bake yang mengharuskan player untuk memanggang adonan tadi supaya menjadi kue yang siap dimakan. Kemudian ruangan decoration untuk langkah terakhir dalam bakery ini yaitu menghias kue tersebut sesuai pesanan pelanggan. Kemudian terdapat UI dalam memudahkan player dalam berpindah ruang. Terdapat juga interaksi antar pelanggan dengan berbicara dengan mereka. Setiap jawaban yang diberikan akan menimbulkan respon yang berbeda.


## Cara Menjalankan Project

Pada tahap awal hingga mendekati penyelesaian pengembangan, game dijalankan melalui berkas main.py. Namun, untuk meningkatkan kemudahan penggunaan bagi pemain serta mendukung proses pengembangan dan distribusi pada tahap selanjutnya, aplikasi kemudian dikonversi menjadi berkas .exe.
Dengan perubahan tersebut, pengguna tidak lagi perlu menjalankan program melalui lingkungan Python. Game dapat langsung dijalankan hanya dengan menekan berkas .exe, sehingga proses penggunaan menjadi lebih praktis dan mudah diakses.

## Penjelasan Implementasi OOP

- Encapsulation

Encapsulation adalah proses membungkus data (atribut) dan fungsi (method) dalam satu class serta mengatur aksesnya menggunakan public dan private agar data lebih aman dan terkontrol.
contoh;
Pada class seperti Cashier, Game, atau SceneManager, terdapat atribut yang diawali dengan underscore (_).
```bash
  class Cashier(Room):
    def __init__(self):
        self._order_ui = OrderUI()
        self._navigation_ui = NavigationUI()
```
atribut:
_order_ui, _navigation_ui
bersifat private karena diawali _.
Artinya atribut tersebut tidak seharusnya diakses langsung dari luar class dan hanya digunakan untuk kebutuhan internal class Cashier.
sedangkan pada method seperti:
update()
render()
handle_event()
bersifat public karna bisa dipanggil dari class lain
- Inheritance

Inheritance adalah pewarisan class.

contoh:

```bash
  class Room(ABC)
```
Diturunkan menjadi:

```bash
  class Cashier(Room)
  class Dough(Room)
  class Decoration(Room)
  class MainMenu(Room)

```

Keuntungan :

- Tidak perlu menulis ulang kode yang sama.
- Semua room memiliki struktur yang seragam.

- Polymorphism

Karena semua room mewarisi Room maka
misalnya:

```bash
  current_room.render()
```
meskipun :

current_room

sedang berisi:

Cashier
Dough
Decoration

Method yang dipanggil adalah

render()

tetapi hasilnya berbeda sesuai room aktif.
Inilah polymorphism.

- Abstraction

Terlihat dari:

```bash
class Room(ABC)
```
dan 

```bash
@abstractmethod

def update()

@abstractmethod

def render()
```

Room hanya menentukan aturan:

update()
render()

dimana implementasinya diserahkan ke subclass



    
## Screenshots Tampilan Program

![App Screenshot](Screenshots/MainMenu.png)
![App Screenshot](Screenshots/Cashier.png)
![App Screenshot](Screenshots/DoughRoom.png)
![App Screenshot](Screenshots/OvenRoom.png)
![App Screenshot](Screenshots/DecorRoom.png)

