"# JVĢ Atribūtikas Internetveikals" 
"""
Lai iedarbinātu programmu nepieciešama virtuālā vide, kuru var izveidot komandrindā rakstot...(bezjēdzīgi rakstīt, ja jūs esat githubā gan jau protat to izveidot)
Ja negribās veidot virtuālo vidi tas nav obligāti, tikai nebrīnaties, ja lejupielādētās bibliotēkas un citi prikoli ietekmē jums nākotnes programmēšanas projektu darbību
Komandrindā jāieraksta "pip install -r requirements.txt"
Jāizveido .env fails, kurā būs FLASK_ENV="development", MAINTENANCE_MODE="false", SECRET_KEY="kaut kāda jūsu slepenā atslēga, parasti uuid4 formātā"
Jāielādē MySQL
Jāizveido jauna lokālā instance
No queries.txt pa vienam jāiekopē MySql workbench queries sadaļā tabulu izveides queriji.
app.py mysql konekcijā (cnx = mysql.connector.connect(user='root', password='#Password1',host='localhost',database='internetveikals')) jāaizvieto vērtības ar savām
komandrindā jāieraksta python app.py
esat internetveikalā(jums tikai nav neviena lietotāja vai produkta)
lai gan varat izveidot jaunu lietotāju, lai izveidotu administratoru, tas jādara manuāli datubāzē, izveidojot jaunu lietotāju, kuram admin laukā ir vērtība 1.
un izveidotajam administratoram jāizveido arī grozs, cart tabulā cart_id ir uuid4 un user_id ir tas pats user_id, kas users tabulā.

Varat eksperimentēt manā neglītajā mājaslapā, lūdzu nelasat kodu, tas ir šausmīgs, es pats tur daudz ko nesaprotu.
"""
