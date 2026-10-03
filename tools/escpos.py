"""Boîte à outils ESC/POS : transforme du texte et des codes-barres en octets.

Imprimante Nigachi (firmware chinois) : sa police ne contient que l'ASCII et le
jeu chinois GB2312, qui inclut é è à ê ù ü. Les autres lettres accentuées
perdent leur accent (ç -> c, ô -> o).
"""
import unicodedata

ESC = b'\x1b'
GS = b'\x1d'

INIT = ESC + b'@'              # réinitialise (reste en mode chinois, voulu)
ALIGN_CENTER = ESC + b'a\x01'  # centre le contenu
BOLD_ON = ESC + b'E\x01'
BOLD_OFF = ESC + b'E\x00'
FEED = ESC + b'd\x04'          # avance le papier de 4 lignes


def _caractere(c):
    """Encode un caractère de la meilleure façon possible pour cette imprimante."""
    if c.isascii():
        return c.encode('ascii')
    try:
        return c.encode('gb2312')      # é è à ê ù ü existent dans la police chinoise
    except UnicodeEncodeError:
        base = unicodedata.normalize('NFKD', c).encode('ascii', 'ignore')
        return base or b'?'            # ç -> c, ô -> o, É -> E


def texte(valeur):
    """Une ligne de texte."""
    return b''.join(_caractere(c) for c in valeur) + b'\n'


def ean13_valide(code):
    """Vrai si le code a 13 chiffres et une clé de contrôle correcte."""
    if len(code) != 13 or not code.isdigit():
        return False
    somme = sum(int(c) * (3 if i % 2 else 1) for i, c in enumerate(code[:12]))
    return (10 - somme % 10) % 10 == int(code[12])


def code_barres(code, hauteur=80, largeur=3, afficher_chiffres=True):
    """EAN-13 si le code est valide, sinon CODE128 (lettres et chiffres)."""
    out = GS + b'h' + bytes([hauteur])
    out += GS + b'H' + (b'\x02' if afficher_chiffres else b'\x00')
    if ean13_valide(code):
        donnees = code[:12].encode('ascii')      # l'imprimante recalcule la clé
        out += GS + b'w' + bytes([largeur])
        out += GS + b'k' + bytes([67, len(donnees)]) + donnees
    else:
        donnees = b'{B' + code.encode('ascii')   # {B = jeu B du CODE128
        out += GS + b'w' + bytes([2])            # plus fin : un CODE128 est plus long
        out += GS + b'k' + bytes([73, len(donnees)]) + donnees
    return out + b'\n'


def etiquette(code, nom=None, prix=None, reference=None, afficher_chiffres=True):
    """Assemble une étiquette complète. Seul le code-barres est obligatoire."""
    out = INIT + ALIGN_CENTER
    if nom:
        out += BOLD_ON + texte(nom) + BOLD_OFF
    if reference:
        out += texte(f"Réf : {reference}")
    out += code_barres(code, afficher_chiffres=afficher_chiffres)
    if prix:
        out += BOLD_ON + texte(prix) + BOLD_OFF
    return out + FEED
