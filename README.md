<div align="center">

# 🎧 LoL Akıllı Ses Asistanı (Automatic Audio Mixer)
### *Oyun Başladığında Sesler Tam İstediğin Seviyeye İnsin, Zafer Senin Olsun!*

[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-00f0ff?style=for-the-badge&logo=windows)](https://github.com)
[![License](https://img.shields.io/badge/Lisans-MIT-ff007f?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-39ff14?style=for-the-badge&logo=python)](https://www.python.org)
[![Build](https://img.shields.io/badge/Tek_Tıkla_Çalışır-Hazır_EXE-ffaa00?style=for-the-badge&logo=quicktime)](https://github.com)

<p align="center">
  <b>League of Legends oynarken arkada bağıran Discord seslerinden veya Spotify'ın oyun sesini bastırmasından bıktınız mı?</b><br>
  Artık Alt+Tab yapıp ses karıştırıcısıyla uğraşmaya son!
</p>

</div>

---

## ⚡ Neden Bu Uygulamayı Kullanmalısınız?

🎮 **Sıfır Çaba, Tam Otomasyon**  
LoL açıldığı anda Discord, Spotify veya dilediğiniz herhangi bir uygulamanın ses seviyesini önceden belirlediğiniz mükemmel kıvama çeker. 

🔄 **Oyun Bittiğinde Eskiye Dönüş (Akıllı Bellek)**  
Maç bittiğinde veya oyunu kapattığınızda, tüm ses seviyeleri oyuna girmeden önceki orijinal durumuna anında geri döner!

🚀 **Kurulum Yok, Tek Tıkla Çalıştır!**  
Karmaşık ayarlarla uğraşmak istemiyorsanız tek bir `.exe` dosyasını indirin ve çift tıklayın. Hepsi bu kadar!

✨ **Ultra Modern Siber/Gamer Arayüzü**  
Göz yormayan şık Neon/Cyber teması, Türkçe & İngilizce tek tıkla dil desteği ve sistem tepsisinde (arka planda) bilgisayarınızı hiç yormadan çalışma yeteneği.

---

## 🌟 Öne Çıkan Özellikler

- **🎯 Akıllı Oyun Algılama:** LoL istemcisi veya maç başladığı saniye devreye girer.
- **🎛️ Özel Ses Kuralları:** Discord'u %65, Spotify'ı %35 yapın ya da istediğiniz oyunu/uygulamayı tek tıkla listeye ekleyin.
- **🤫 Tek Tıkla Susturma (Mute):** İsterseniz oyun sırasında belirli programların sesini tamamen kesin.
- **🛡️ Manuel Müdahale Koruması:** Oyun sırasında ses ayarını kendiniz değiştirirseniz sizi engellemez, kontrol daima sizde kalır.
- **🎈 Arka Planda Sessizce Çalışır:** Sistem tepsisine küçülür, performanstan ve FPS'ten asla ödün vermez.

---

## 📥 Hemen İndirin ve Kullanmaya Başlayın!

1. [Releases](../../releases) sayfasından en güncel **`LoLAutomaticAudioMixer.exe`** dosyasını indirin.
2. Çift tıklayarak başlatın.
3. Dilediğiniz ses seviyelerini ayarlayın veya varsayılan ayarlarla doğrudan oyuna girin!
4. **Tadını Çıkarın:** Arkada çalan şarkılar ve takım arkadaşlarınızın sesi artık tam duymak istediğiniz netlikte!

---

## 💻 Geliştiriciler İçin (Kaynak Koddan Çalıştırma)

Projeyi kendi bilgisayarınızda geliştirmek veya kaynak koddan derlemek isterseniz:

```powershell
# 1. Projeyi klonlayın
git clone https://github.com/KULLANICI_ADINIZ/lol-automatic-audio-mixer.git
cd lol-automatic-audio-mixer

# 2. Gerekli kütüphaneleri yükleyin
py -m pip install -r requirements.txt

# 3. Uygulamayı başlatın
py main.py
```

### 🔨 Kendi Tek EXE Dosyanızı Üretin:
```powershell
py -m pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name "LoLAutomaticAudioMixer" --icon "mixer_app/resources/icon.ico" --add-data "mixer_app/resources;mixer_app/resources" main.py
```

---

## 📄 Lisans

Bu proje özgür ve açık kaynaklıdır; **MIT Lisansı** ile lisanslanmıştır. 
