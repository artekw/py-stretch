import os
import shutil
import random
import string
import logging
import tornado.ioloop
import tornado.web
import tornado.websocket

import pystretch

img_name = ''
clients = []

# rozmiar formatów
# szer x wys w pikselach 300dpi
# A4 = (2480, 3508)
# A3 = (3508, 4961)
# A2 = (4961, 7016)
# A1 = (7016, 9933)
# A0 = (9933, 14043)


def send_to_all_clients(message):
    for client in clients:
        if not client.ws_connection.stream.socket:
            print("Web socket does not exist anymore!!!")
            clients.remove(client)
        else:
            client.write_message(message)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        alert = None
        send_to_all_clients("Open con")
        # alert = {"type": "info", "msg":"info alert"}
        self.render("home.html", alert=alert)


class ConvertHandler(tornado.web.RequestHandler):
    def get(self):
        logs = []
        download_url = ''

        base = os.getcwd()
        temp_dir = base + '/tmp'

        # size url paramater
        size_user = self.get_argument('size')
        if size_user == "A0":
            size = (9933, 14043)
        elif size_user == "A1":
            size = (7016, 9933)
        elif size_user == "A2":
            size = (4961, 7016)
        elif size_user == "A3":
            size = (3508, 4961)
        else:
            size = (2480, 3508)

        sesion_hastag = pystretch.hashtag()
        sesion_folder = '{0}/{1}'.format(temp_dir, sesion_hastag)
        os.mkdir(sesion_folder)
        logging.info("Utworzono katalog tymczasowy" + sesion_folder)


        filename, filename_ext = os.path.splitext(img_name)
        pystretch.resize_image(
            temp_dir + "/" + img_name, size, '{0}/{1}_resized{2}'.format(sesion_folder, filename, filename_ext))

        # logasyncging.info("Obrazek został przeskalowany")
        # logs.append("Obrazek został przeskalowany")
        # send_to_all_clients("Obrazek został przeskalowany...")

        if size_user == "A3":
            pystretch.cut_image(
                '{0}/{1}_resized{2}'.format(sesion_folder, filename, filename_ext), 3508, 2480)
        else:
            pystretch.cut_image(
                '{0}/{1}_resized{2}'.format(sesion_folder, filename, filename_ext), 2480, 3508)

        # logging.info("Obrazek został pociety na kawałki")
        # send_to_all_clients("Obrazek został pociety na kawałki...")
        # logs.append("Obrazek został pociety na kawałki")


        paths = [sesion_folder + '/' +
                 pdf for pdf in os.listdir(sesion_folder)]

        pystretch.merge_pdf(base + '/static/data/' + filename, paths)
        # send_to_all_clients("Generowanie plik PDF...")
        # logs.append("Generowanie plik PDF...")

        download_url = '{}://{}/static/data/{}.pdf'.format(self.request.protocol, self.request.host, filename)

        self.render("convert.html", url=download_url)


class UploadHandler(tornado.web.RequestHandler):
    def post(self):
        alert = False
        uploaded_file = None

        #check if user choose file
        try:
            uploaded_file = self.request.files['uploaded_file'][0]
        except KeyError:         
            alert_msg = {"type": "warning", "msg": "Wybierz plik obrazka"}
            self.render("home.html", alert_msg=alert_msg)
            alert = True

        # check extension of uploaded file
        if uploaded_file != None:
            allowed_extensions = [".jpg", ".png", ".gif"]
            extension_uploaded_file = os.path.splitext(uploaded_file['filename'])[1]

            if extension_uploaded_file not in allowed_extensions:
                alert_msg = {"type": "warning",
                        "msg": "Nieobsługiwany format pliku. Wymagany jest obraz z rozszerzeniem " + " ".join(allowed_extensions)}
                self.render("home.html", alert_msg=alert_msg)
                alert = True

        # pdf file name
        pdf_file_name = self.get_argument('pdf_file')
        

        # check if user choose image size
        try:
            size = self.get_argument('size')
        except tornado.web.MissingArgumentError:
            alert_msg = {"type": "warning", "msg": "Wybierz rozmiar plakatu"}
            self.render("home.html", alert_msg=alert_msg)
            alert = True

        if not alert:
            logging.info("Wybrano format " + size)
            original_fname = uploaded_file['filename']
            if pdf_file_name:
                final_filename = pdf_file_name+extension_uploaded_file
            else:
                fname = ''.join(random.choice(
                    string.ascii_lowercase + string.digits) for x in range(6))
                final_filename = fname+extension_uploaded_file
            global img_name
            img_name = final_filename
            with open("tmp/" + final_filename, 'wb') as f:
                f.write(uploaded_file['body'])
                f.close()
            #self.finish("file" + final_filename + " wysłany")
            logging.info("Zapisano plik" + final_filename)
            self.redirect("/convert?size=" + size)


class MessagesWS(tornado.websocket.WebSocketHandler):
    def open(self):
        print("WebSocket opened")
        if self not in clients:
            clients.append(self)

    # def on_message(self, message):
    #     send_to_all_clients("new client")
    #     for client in clients:
    #         if self ot in clients:
    #             client.write_message("ECHO: " + message)

    def on_close(self):
        print("WebSocket closed")
        if self in clients:
            clients.remove(self)


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/upload", UploadHandler),
        (r"/convert", ConvertHandler),
        (r'/websocket', MessagesWS),
        (r'/favicon.ico', tornado.web.StaticFileHandler,
         {'path': os.path.join(os.path.dirname(__file__), "static")}),
    ],
        template_path=os.path.join(os.path.dirname(__file__), "views"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=True,
        autoreload=True)


if __name__ == "__main__":
    base = os.getcwd()
    temp_dir = base + '/tmp'
    data_dir = base + '/static/data'

    if not os.path.isdir(temp_dir):
        logging.info("Tworze katalog plików tymczasowych")
        os.mkdir(temp_dir)
    else:
        # delete and create clean folder
        shutil.rmtree(temp_dir)
        os.mkdir(temp_dir)

    if not os.path.isdir(data_dir):
        logging.info("Tworze katalog plików aplikacji")
        os.mkdir(data_dir)
    else:
        # delete and create clean folder
        shutil.rmtree(data_dir)
        os.mkdir(data_dir)
    

    app = make_app()
    app.listen(int(os.environ.get('PORT', '5000')))
    print("Start app")
    tornado.ioloop.IOLoop.current().start()
