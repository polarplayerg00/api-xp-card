from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

app = Flask(__name__)

# Usar uma fonte padrão
FONT_SIZE = 24
LEVEL_FONT_SIZE = 18
NAME_COLOR = (255, 105, 180)
BAR_COLOR = (255, 105, 180)
BG_COLOR = (54, 57, 63)

@app.route('/generate-card')
def generate_card():
    # Parâmetros da query
    avatar_url = request.args.get('avatar')
    banner_url = request.args.get('banner')
    name = request.args.get('nome', 'User')
    level = request.args.get('level', '1')
    xp_current = int(request.args.get('xp_atual', '0'))
    xp_max = int(request.args.get('xp_max', '100'))
    name_color = request.args.get('cor_texto', '#FF69B4')
    bar_color = request.args.get('cor_barra', '#FF69B4')
    
    # Convertendo cores HEX para RGB
    name_color = tuple(int(name_color[i:i+2], 16) for i in (1, 3, 5))
    bar_color = tuple(int(bar_color[i:i+2], 16) for i in (1, 3, 5))

    # Tamanho do card
    card_width = 600
    card_height = 240
    
    # Criar a imagem de fundo
    card = Image.new('RGB', (card_width, card_height), BG_COLOR)
    draw = ImageDraw.Draw(card)
    
    # Carregar o banner de fundo
    response = requests.get(banner_url)
    banner = Image.open(BytesIO(response.content)).resize((card_width, card_height))
    card.paste(banner, (0, 0))
    
    # Desenhar a barra de XP
    bar_width = 400
    bar_height = 20
    bar_x = 160
    bar_y = 160
    draw.rectangle([(bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height)], fill=(80, 80, 80)) # Barra de fundo
    filled_width = int((xp_current / xp_max) * bar_width)
    draw.rectangle([(bar_x, bar_y), (bar_x + filled_width, bar_y + bar_height)], fill=bar_color) # Barra preenchida
    
    # Usar fonte padrão do sistema
    try:
        font = ImageFont.load_default()
        level_font = ImageFont.load_default()
    except Exception as e:
        return f"Erro ao carregar fonte: {e}", 500
    
    # Desenhar o nome e nível
    draw.text((160, 120), name, font=font, fill=name_color)
    draw.text((card_width - 100, 170), f"Level - {level}", font=level_font, fill=name_color)
    
    # Desenhar o texto de XP
    draw.text((card_width - 120, 200), f"{xp_current}/{xp_max}", font=level_font, fill=name_color)
    
    # Carregar e desenhar o avatar
    response = requests.get(avatar_url)
    avatar = Image.open(BytesIO(response.content)).resize((128, 128))
    avatar = avatar.convert("RGBA")
    
    # Criar uma máscara circular para o avatar
    mask = Image.new('L', avatar.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, 128, 128), fill=255)
    card.paste(avatar, (20, 20), mask)
    
    # Salvar a imagem em memória
    output = BytesIO()
    card.save(output, format='PNG')
    output.seek(0)
    
    return send_file(output, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
