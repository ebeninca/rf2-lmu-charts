# Mapeamento de circuitos para códigos de país (ISO 3166-1 alpha-2)
TRACK_COUNTRY_MAP = {
    # Circuitos conhecidos
    'Spa': 'BE',  # Bélgica
    'Monza': 'IT',  # Itália
    'Silverstone': 'GB',  # Reino Unido
    'Nürburgring': 'DE',  # Alemanha
    'Nurburgring': 'DE',
    'Hockenheim': 'DE',
    'Barcelona': 'ES',  # Espanha
    'Catalunya': 'ES',
    'Paul Ricard': 'FR',  # França
    'Ricard': 'FR',
    'Le Castellet': 'FR',
    'Le Mans': 'FR',
    'Magny-Cours': 'FR',
    'Imola': 'IT',
    'Mugello': 'IT',
    'Misano': 'IT',
    'Brands Hatch': 'GB',
    'Donington': 'GB',
    'Snetterton': 'GB',
    'Oulton Park': 'GB',
    'Zandvoort': 'NL',  # Holanda
    'Zolder': 'BE',
    'Red Bull Ring': 'AT',  # Áustria
    'Spielberg': 'AT',
    'Hungaroring': 'HU',  # Hungria
    'Portimão': 'PT',  # Portugal
    'Portimao': 'PT',
    'Estoril': 'PT',
    'Interlagos': 'BR',  # Brasil
    'Suzuka': 'JP',  # Japão
    'Fuji': 'JP',
    'Sebring': 'US',  # EUA
    'Daytona': 'US',
    'Watkins Glen': 'US',
    'Road America': 'US',
    'Road Atlanta': 'US',
    'Laguna Seca': 'US',
    'Indianapolis': 'US',
    'COTA': 'US',
    'Circuit of the Americas': 'US',
    'Bathurst': 'AU',  # Austrália
    'Albert Park': 'AU',
    'Phillip Island': 'AU',
    'Kyalami': 'ZA',  # África do Sul
    'Yas Marina': 'AE',  # Emirados Árabes
    'Bahrain': 'BH',  # Bahrein
    'Sepang': 'MY',  # Malásia
    'Singapore': 'SG',  # Singapura
    'Shanghai': 'CN',  # China
    'Jerez': 'ES',
    'Valencia': 'ES',
    'Monteblanco': 'ES',
    'Oschersleben': 'DE',
    'Lausitzring': 'DE',
    'Sachsenring': 'DE',
    'Salzburgring': 'AT',
    'Most': 'CZ',  # República Tcheca
    'Brno': 'CZ',
    'Slovakiaring': 'SK',  # Eslováquia
}

# Mapeamento de códigos de país para nomes em inglês
COUNTRY_NAMES = {
    'BE': 'Belgium',
    'IT': 'Italy',
    'GB': 'United Kingdom',
    'DE': 'Germany',
    'ES': 'Spain',
    'FR': 'France',
    'NL': 'Netherlands',
    'AT': 'Austria',
    'HU': 'Hungary',
    'PT': 'Portugal',
    'BR': 'Brazil',
    'JP': 'Japan',
    'US': 'United States',
    'AU': 'Australia',
    'ZA': 'South Africa',
    'AE': 'United Arab Emirates',
    'BH': 'Bahrain',
    'MY': 'Malaysia',
    'SG': 'Singapore',
    'CN': 'China',
    'CZ': 'Czech Republic',
    'SK': 'Slovakia',
}

def get_country_flag(track_name):
    """Retorna o código do país baseado no nome do circuito"""
    if not track_name or track_name == 'Unknown':
        return '', ''
    # Procura por match parcial no nome do circuito
    for circuit, country_code in TRACK_COUNTRY_MAP.items():
        if circuit.lower() in track_name.lower():
            country_name = COUNTRY_NAMES.get(country_code, country_code)
            return country_code, country_name
    return '', ''  # Retorna vazio se não encontrar
