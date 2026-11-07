#!/usr/bin/env python3
"""
Graficzny generator komend TRIM i montowania dla Linuksa (pygame).
Program NIC nie uruchamia. Kliknięcie komendy kopiuje ją do schowka,
a użytkownik sam wkleja ją w terminal.
"""
import shutil
import subprocess
import time

import pygame

# (nazwa, komenda, opis, kategoria)
SZABLONY = [
    ("TRIM wszystkich dysków SSD", "sudo fstrim -a",
     "Wysyła TRIM do wszystkich zamontowanych dysków SSD.", "TRIM"),
    ("TRIM z podsumowaniem", "sudo fstrim -av",
     "Jak wyżej, ale pokazuje, ile miejsca zwolniono na każdym dysku.", "TRIM"),
    ("Które dyski to SSD?", "lsblk -d -o NAME,ROTA,SIZE,MODEL",
     "ROTA = 0 oznacza SSD, ROTA = 1 oznacza dysk talerzowy HDD.", "INFO"),
    ("Automatyczny TRIM", "systemctl status fstrim.timer",
     "Pokazuje, czy system sam robi TRIM raz w tygodniu.", "INFO"),
    ("Lista wszystkich partycji", "lsblk -f",
     "Pokazuje dyski i partycje, ich systemy plików i punkty montowania.", "MONTOWANIE"),
    ("Zamontuj wszystko z fstab", "sudo mount -a",
     "Montuje wpisy z /etc/fstab, które jeszcze nie są zamontowane.", "MONTOWANIE"),
]

SZEROKOSC, WYSOKOSC = 780, 620
TLO = (245, 246, 250)
PASEK = (28, 32, 48)
BIALY = (255, 255, 255)
CZARNY = (25, 25, 30)
SZARY = (120, 124, 135)
JASNY_SZARY = (226, 228, 236)
NIEBIESKI = (66, 120, 230)
NIEBIESKI_JASNY = (225, 234, 252)
ZIELONY = (30, 150, 85)
KOD_TLO = (240, 248, 243)
KATEGORIE_KOLOR = {"TRIM": (230, 120, 40), "INFO": (60, 130, 200), "MONTOWANIE": (130, 80, 200)}


def kopiuj_do_schowka(tekst):
    """Próbuje skopiować tekst do schowka. Zwraca True, jeśli się udało."""
    polecenia = [
        ["wl-copy"],               # Wayland
        ["xclip", "-selection", "clipboard"],  # X11
        ["xsel", "--clipboard", "--input"],    # X11 alternatywa
    ]
    for polecenie in polecenia:
        if shutil.which(polecenie[0]):
            try:
                subprocess.run(polecenie, input=tekst.encode(), check=True)
                return True
            except (subprocess.CalledProcessError, OSError):
                pass
    return False


def zaokraglony(ekran, kolor, prostokat, promien=10, ramka=0, kolor_ramki=None):
    pygame.draw.rect(ekran, kolor, prostokat, border_radius=promien)
    if ramka and kolor_ramki:
        pygame.draw.rect(ekran, kolor_ramki, prostokat, width=ramka, border_radius=promien)


def main():
    pygame.init()
    ekran = pygame.display.set_mode((SZEROKOSC, WYSOKOSC))
    pygame.display.set_caption("Generator komend TRIM i montowania")
    tytul = pygame.font.SysFont("dejavusans", 26, bold=True)
    czcionka = pygame.font.SysFont("dejavusans", 19)
    maly = pygame.font.SysFont("dejavusans", 15)
    mikro = pygame.font.SysFont("dejavusans", 12, bold=True)
    kod = pygame.font.SysFont("dejavusansmono", 18, bold=True)
    zegar = pygame.time.Clock()

    przyciski = [pygame.Rect(30, 130 + i * 62, 720, 52) for i in range(len(SZABLONY))]
    panel_kod = pygame.Rect(50, 540, 680, 40)
    wybrany = None
    kursor = (0, 0)
    komunikat = ""
    komunikat_do = 0.0

    while True:
        for zdarzenie in pygame.event.get():
            if zdarzenie.type == pygame.QUIT:
                pygame.quit()
                return
            if zdarzenie.type == pygame.KEYDOWN and zdarzenie.key == pygame.K_ESCAPE:
                pygame.quit()
                return
            if zdarzenie.type == pygame.MOUSEMOTION:
                kursor = zdarzenie.pos
            if zdarzenie.type == pygame.MOUSEBUTTONDOWN and zdarzenie.button == 1:
                for i, prostokat in enumerate(przyciski):
                    if prostokat.collidepoint(zdarzenie.pos):
                        wybrany = i
                # Kliknięcie w komendę kopiuje ją do schowka
                if wybrany is not None and panel_kod.collidepoint(zdarzenie.pos):
                    komenda = SZABLONY[wybrany][1]
                    if kopiuj_do_schowka(komenda):
                        komunikat = "Skopiowano do schowka"
                    else:
                        komunikat = "Brak xclip lub wl-copy: sudo apt install xclip"
                    komunikat_do = time.time() + 2.0

        ekran.fill(TLO)

        # Pasek nagłówka
        pygame.draw.rect(ekran, PASEK, (0, 0, SZEROKOSC, 100))
        ekran.blit(tytul.render("Generator komend TRIM i montowania", True, BIALY), (30, 22))
        ekran.blit(maly.render("Wybierz akcję, kliknij komendę, żeby ją skopiować. ESC zamyka program.", True, (190, 196, 215)), (30, 62))

        # Przyciski z efektem najechania
        for i, (nazwa, _, _, kategoria) in enumerate(SZABLONY):
            prostokat = przyciski[i]
            najechany = prostokat.collidepoint(kursor)
            aktywny = i == wybrany
            if aktywny:
                tlo = NIEBIESKI
            elif najechany:
                tlo = NIEBIESKI_JASNY
            else:
                tlo = BIALY
            zaokraglony(ekran, tlo, prostokat, 10, 1, JASNY_SZARY)

            znacznik = pygame.Rect(prostokat.x + 14, prostokat.y + 18, 10, 16)
            pygame.draw.rect(ekran, KATEGORIE_KOLOR[kategoria], znacznik, border_radius=4)

            ekran.blit(czcionka.render(nazwa, True, BIALY if aktywny else CZARNY), (prostokat.x + 36, prostokat.y + 14))
            etykieta = mikro.render(kategoria, True, BIALY if aktywny else SZARY)
            ekran.blit(etykieta, (prostokat.right - etykieta.get_width() - 14, prostokat.y + 18))

        # Panel z wynikiem
        panel = pygame.Rect(30, 500, 720, 100)
        zaokraglony(ekran, BIALY, panel, 12, 1, JASNY_SZARY)
        if wybrany is None:
            ekran.blit(maly.render("Kliknij jedną z akcji powyżej.", True, SZARY), (50, 530))
        else:
            nazwa, komenda, opis, _ = SZABLONY[wybrany]
            ekran.blit(maly.render(opis, True, CZARNY), (50, 512))
            zaokraglony(ekran, KOD_TLO, panel_kod, 8)
            ekran.blit(kod.render(komenda, True, ZIELONY), (66, 548))
            ekran.blit(mikro.render("Kliknij komendę, żeby ją skopiować. Program niczego nie uruchomił.", True, SZARY), (50, 586))

        # Komunikat o skopiowaniu (znika po 2 sekundach)
        if komunikat and time.time() < komunikat_do:
            kolor = ZIELONY if komunikat.startswith("Skopiowano") else (200, 60, 60)
            ekran.blit(czcionka.render(komunikat, True, kolor), (30, 606 - 20))

        pygame.display.flip()
        zegar.tick(30)


if __name__ == "__main__":
    main()