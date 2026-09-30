"""Gera as imagens didáticas do Post 5 usando apenas a biblioteca padrão.
Execute: python3 post-5/gerar-imagens.py
"""
from math import hypot
from pathlib import Path

WIDTH, HEIGHT = 240, 140
GX = ((-1, 0, 1), (-2, 0, 2), (-1, 0, 1))
GY = ((-1, -2, -1), (0, 0, 0), (1, 2, 1))


def sobel(pixels):
    """Magnitude do gradiente, replicando os pixels nas margens."""
    height, width = len(pixels), len(pixels[0])
    result = []
    for y in range(height):
        row = []
        for x in range(width):
            gx = gy = 0
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    value = pixels[min(height - 1, max(0, y + dy))][min(width - 1, max(0, x + dx))]
                    gx += value * GX[dy + 1][dx + 1]
                    gy += value * GY[dy + 1][dx + 1]
            row.append(hypot(gx, gy))
        result.append(row)
    return result


def save_svg(path, pixels, title):
    """Agrupa pixels consecutivos da mesma intensidade em retângulos."""
    height, width = len(pixels), len(pixels[0])
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" shape-rendering="crispEdges">', f'<title>{title}</title>']
    for y, row in enumerate(pixels):
        x = 0
        while x < width:
            end = x + 1
            while end < width and row[end] == row[x]:
                end += 1
            shade = f'{row[x]:02x}' * 3
            parts.append(f'<path fill="#{shade}" d="M{x} {y}h{end-x}v1H{x}z"/>')
            x = end
    path.write_text('\n'.join(parts) + '\n</svg>\n')


def main():
    pixels = [[200 if (x - 174) ** 2 + (y - 70) ** 2 <= 37 ** 2 else
               140 if 25 <= x < 100 and 30 <= y < 110 else 20
               for x in range(WIDTH)] for y in range(HEIGHT)]
    magnitude = sobel(pixels)
    peak = max(map(max, magnitude))
    edges = [[round(value * 255 / peak) for value in row] for row in magnitude]
    folder = Path(__file__).parent / 'imagens'
    folder.mkdir(exist_ok=True)
    save_svg(folder / 'original.svg', pixels, 'Imagem original: retângulo e círculo sobre fundo escuro')
    save_svg(folder / 'bordas.svg', edges, 'Magnitude do gradiente calculada com Sobel')


if __name__ == '__main__':
    main()
