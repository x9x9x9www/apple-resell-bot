const POPULAR_TEMPLATES = [
  {
    "id": "iphone",
    "name": "iPhone",
    "icon": "📱",
    "models": [
      {
        "model": "iPhone 16 Pro Max",
        "storage": 256,
        "price": 105000,
        "market": 126000
      },
      {
        "model": "iPhone 16 Pro Max",
        "storage": 512,
        "price": 118000,
        "market": 141600
      },
      {
        "model": "iPhone 16 Pro Max",
        "storage": 1024,
        "price": 132000,
        "market": 158400
      },
      {
        "model": "iPhone 16 Pro",
        "storage": 128,
        "price": 88000,
        "market": 105600
      },
      {
        "model": "iPhone 16 Pro",
        "storage": 256,
        "price": 96000,
        "market": 115200
      },
      {
        "model": "iPhone 16 Pro",
        "storage": 512,
        "price": 108000,
        "market": 129600
      },
      {
        "model": "iPhone 16 Pro",
        "storage": 1024,
        "price": 120000,
        "market": 144000
      },
      {
        "model": "iPhone 16 Plus",
        "storage": 128,
        "price": 72000,
        "market": 86400
      },
      {
        "model": "iPhone 16 Plus",
        "storage": 256,
        "price": 76000,
        "market": 91200
      },
      {
        "model": "iPhone 16 Plus",
        "storage": 512,
        "price": 85000,
        "market": 102000
      },
      {
        "model": "iPhone 16",
        "storage": 128,
        "price": 68000,
        "market": 81600
      },
      {
        "model": "iPhone 16",
        "storage": 256,
        "price": 68000,
        "market": 81600
      },
      {
        "model": "iPhone 16",
        "storage": 512,
        "price": 78000,
        "market": 93600
      },
      {
        "model": "iPhone 15 Pro Max",
        "storage": 256,
        "price": 82000,
        "market": 98400
      },
      {
        "model": "iPhone 15 Pro Max",
        "storage": 512,
        "price": 84000,
        "market": 100800
      },
      {
        "model": "iPhone 15 Pro Max",
        "storage": 1024,
        "price": 94000,
        "market": 112800
      },
      {
        "model": "iPhone 15 Pro",
        "storage": 128,
        "price": 65000,
        "market": 78000
      },
      {
        "model": "iPhone 15 Pro",
        "storage": 256,
        "price": 72000,
        "market": 86400
      },
      {
        "model": "iPhone 15 Pro",
        "storage": 512,
        "price": 72000,
        "market": 86400
      },
      {
        "model": "iPhone 15 Pro",
        "storage": 1024,
        "price": 80000,
        "market": 96000
      },
      {
        "model": "iPhone 15 Plus",
        "storage": 128,
        "price": 48000,
        "market": 57600
      },
      {
        "model": "iPhone 15 Plus",
        "storage": 256,
        "price": 54000,
        "market": 64800
      },
      {
        "model": "iPhone 15 Plus",
        "storage": 512,
        "price": 62000,
        "market": 74400
      },
      {
        "model": "iPhone 15",
        "storage": 128,
        "price": 50000,
        "market": 60000
      },
      {
        "model": "iPhone 15",
        "storage": 256,
        "price": 50000,
        "market": 60000
      },
      {
        "model": "iPhone 15",
        "storage": 512,
        "price": 58000,
        "market": 69600
      },
      {
        "model": "iPhone 14 Pro Max",
        "storage": 128,
        "price": 58000,
        "market": 69600
      },
      {
        "model": "iPhone 14 Pro Max",
        "storage": 256,
        "price": 62000,
        "market": 74400
      },
      {
        "model": "iPhone 14 Pro Max",
        "storage": 512,
        "price": 69000,
        "market": 82800
      },
      {
        "model": "iPhone 14 Pro Max",
        "storage": 1024,
        "price": 76000,
        "market": 91200
      },
      {
        "model": "iPhone 14 Pro",
        "storage": 128,
        "price": 50000,
        "market": 60000
      },
      {
        "model": "iPhone 14 Pro",
        "storage": 256,
        "price": 53000,
        "market": 63600
      },
      {
        "model": "iPhone 14 Pro",
        "storage": 512,
        "price": 59000,
        "market": 70800
      },
      {
        "model": "iPhone 14 Pro",
        "storage": 1024,
        "price": 65000,
        "market": 78000
      },
      {
        "model": "iPhone 14 Plus",
        "storage": 128,
        "price": 38000,
        "market": 45600
      },
      {
        "model": "iPhone 14 Plus",
        "storage": 256,
        "price": 43000,
        "market": 51600
      },
      {
        "model": "iPhone 14 Plus",
        "storage": 512,
        "price": 49000,
        "market": 58800
      },
      {
        "model": "iPhone 14",
        "storage": 128,
        "price": 40000,
        "market": 48000
      },
      {
        "model": "iPhone 14",
        "storage": 256,
        "price": 40000,
        "market": 48000
      },
      {
        "model": "iPhone 14",
        "storage": 512,
        "price": 46000,
        "market": 55200
      },
      {
        "model": "iPhone 13 Pro Max",
        "storage": 128,
        "price": 46000,
        "market": 55200
      },
      {
        "model": "iPhone 13 Pro Max",
        "storage": 256,
        "price": 50000,
        "market": 60000
      },
      {
        "model": "iPhone 13 Pro Max",
        "storage": 512,
        "price": 56000,
        "market": 67200
      },
      {
        "model": "iPhone 13 Pro Max",
        "storage": 1024,
        "price": 62000,
        "market": 74400
      },
      {
        "model": "iPhone 13 Pro",
        "storage": 128,
        "price": 38000,
        "market": 45600
      },
      {
        "model": "iPhone 13 Pro",
        "storage": 256,
        "price": 43000,
        "market": 51600
      },
      {
        "model": "iPhone 13 Pro",
        "storage": 512,
        "price": 48000,
        "market": 57600
      },
      {
        "model": "iPhone 13 Pro",
        "storage": 1024,
        "price": 53000,
        "market": 63600
      },
      {
        "model": "iPhone 13",
        "storage": 128,
        "price": 32000,
        "market": 38400
      },
      {
        "model": "iPhone 13",
        "storage": 256,
        "price": 34000,
        "market": 40800
      },
      {
        "model": "iPhone 13",
        "storage": 512,
        "price": 39000,
        "market": 46800
      },
      {
        "model": "iPhone 13 mini",
        "storage": 128,
        "price": 27000,
        "market": 32400
      },
      {
        "model": "iPhone 13 mini",
        "storage": 256,
        "price": 31000,
        "market": 37200
      },
      {
        "model": "iPhone 13 mini",
        "storage": 512,
        "price": 36000,
        "market": 43200
      },
      {
        "model": "iPhone 12 Pro Max",
        "storage": 128,
        "price": 33000,
        "market": 39600
      },
      {
        "model": "iPhone 12 Pro Max",
        "storage": 256,
        "price": 37000,
        "market": 44400
      },
      {
        "model": "iPhone 12 Pro Max",
        "storage": 512,
        "price": 42000,
        "market": 50400
      },
      {
        "model": "iPhone 12 Pro",
        "storage": 128,
        "price": 27000,
        "market": 32400
      },
      {
        "model": "iPhone 12 Pro",
        "storage": 256,
        "price": 31000,
        "market": 37200
      },
      {
        "model": "iPhone 12 Pro",
        "storage": 512,
        "price": 35000,
        "market": 42000
      },
      {
        "model": "iPhone 12",
        "storage": 64,
        "price": 18000,
        "market": 21600
      },
      {
        "model": "iPhone 12",
        "storage": 128,
        "price": 23000,
        "market": 27600
      },
      {
        "model": "iPhone 12",
        "storage": 256,
        "price": 25000,
        "market": 30000
      },
      {
        "model": "iPhone 12 mini",
        "storage": 64,
        "price": 16000,
        "market": 19200
      },
      {
        "model": "iPhone 12 mini",
        "storage": 128,
        "price": 19000,
        "market": 22800
      },
      {
        "model": "iPhone 12 mini",
        "storage": 256,
        "price": 22000,
        "market": 26400
      },
      {
        "model": "iPhone 11 Pro Max",
        "storage": 64,
        "price": 22000,
        "market": 26400
      },
      {
        "model": "iPhone 11 Pro Max",
        "storage": 256,
        "price": 26000,
        "market": 31200
      },
      {
        "model": "iPhone 11 Pro Max",
        "storage": 512,
        "price": 29000,
        "market": 34800
      },
      {
        "model": "iPhone 11 Pro",
        "storage": 64,
        "price": 18000,
        "market": 21600
      },
      {
        "model": "iPhone 11 Pro",
        "storage": 256,
        "price": 22000,
        "market": 26400
      },
      {
        "model": "iPhone 11 Pro",
        "storage": 512,
        "price": 25000,
        "market": 30000
      },
      {
        "model": "iPhone 11",
        "storage": 64,
        "price": 13000,
        "market": 15600
      },
      {
        "model": "iPhone 11",
        "storage": 128,
        "price": 16000,
        "market": 19200
      },
      {
        "model": "iPhone 11",
        "storage": 256,
        "price": 19000,
        "market": 22800
      }
    ]
  },
  {
    "id": "samsung",
    "name": "Samsung",
    "icon": "📱",
    "models": [
      {
        "model": "Samsung Galaxy S24 Ultra",
        "storage": 256,
        "price": 65000,
        "market": 78000
      },
      {
        "model": "Samsung Galaxy S24 Ultra",
        "storage": 512,
        "price": 74000,
        "market": 88000
      },
      {
        "model": "Samsung Galaxy S24 Ultra",
        "storage": 1024,
        "price": 90000,
        "market": 110000
      },
      {
        "model": "Samsung Galaxy S24",
        "storage": 128,
        "price": 42000,
        "market": 51000
      },
      {
        "model": "Samsung Galaxy S24",
        "storage": 256,
        "price": 47000,
        "market": 58000
      },
      {
        "model": "Samsung Galaxy S23 Ultra",
        "storage": 256,
        "price": 48000,
        "market": 58000
      },
      {
        "model": "Samsung Galaxy S23 Ultra",
        "storage": 512,
        "price": 59000,
        "market": 72000
      },
      {
        "model": "Samsung Galaxy S23",
        "storage": 128,
        "price": 33000,
        "market": 42000
      },
      {
        "model": "Samsung Galaxy S23",
        "storage": 256,
        "price": 37000,
        "market": 47000
      },
      {
        "model": "Samsung Galaxy S24+",
        "storage": 256,
        "price": 50000,
        "market": 60000
      },
      {
        "model": "Samsung Galaxy Z Fold 5",
        "storage": 256,
        "price": 58000,
        "market": 70000
      }
    ]
  },
  {
    "id": "pixel",
    "name": "Pixel",
    "icon": "📱",
    "models": [
      {
        "model": "Google Pixel 9 Pro",
        "storage": 128,
        "price": 58000,
        "market": 69600
      },
      {
        "model": "Google Pixel 9 Pro",
        "storage": 256,
        "price": 70000,
        "market": 84000
      },
      {
        "model": "Google Pixel 9",
        "storage": 128,
        "price": 45000,
        "market": 54000
      },
      {
        "model": "Google Pixel 9",
        "storage": 256,
        "price": 51000,
        "market": 61200
      },
      {
        "model": "Google Pixel 8 Pro",
        "storage": 128,
        "price": 42000,
        "market": 50400
      },
      {
        "model": "Google Pixel 8 Pro",
        "storage": 256,
        "price": 48000,
        "market": 57600
      },
      {
        "model": "Google Pixel 8",
        "storage": 128,
        "price": 30000,
        "market": 36000
      },
      {
        "model": "Google Pixel 8",
        "storage": 256,
        "price": 35000,
        "market": 42000
      },
      {
        "model": "Google Pixel 7 Pro",
        "storage": 128,
        "price": 27000,
        "market": 32400
      }
    ]
  },
  {
    "id": "macbook",
    "name": "Mac",
    "icon": "💻",
    "models": [
      {
        "model": "MacBook Air M1",
        "storage": 256,
        "price": 42000,
        "market": 52000
      },
      {
        "model": "MacBook Air M1",
        "storage": 512,
        "price": 55000,
        "market": 66000
      },
      {
        "model": "MacBook Air M2 13",
        "storage": 256,
        "price": 62000,
        "market": 74000
      },
      {
        "model": "MacBook Air M2 13",
        "storage": 512,
        "price": 75000,
        "market": 92000
      },
      {
        "model": "MacBook Pro 14 M1 Pro",
        "storage": 512,
        "price": 85000,
        "market": 102000
      },
      {
        "model": "MacBook Pro 14 M1 Pro",
        "storage": 1024,
        "price": 100000,
        "market": 122000
      },
      {
        "model": "MacBook Pro 16 M1 Pro",
        "storage": 512,
        "price": 98000,
        "market": 118000
      }
    ]
  }
];