# to create webserver
from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi

# to perform CRUD
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
# from sqlalchemy.ext.declarative import declarative_base

# create DB Session 		
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

class WebServerHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			if self.path.endswith("/restaurant"):
				self.send_response(200)
				self.send_header('Content-type','text/html')
				self.end_headers()

				data = session.query(Restaurant).all()

				output = ""
				output += "<html><body>"

				for row in data:
					print(row.name + '\n ')
					output += '<b>' + row.name + '</b> <br />'
					output += "<a href='/restaurant/" + str(row.id) + "/update'> Edit</a>"
					output += "&emsp;"
					output += "<a href='/restaurant/" + str(row.id) + "/delete'> Delete</a>" 
					output += '<br /><br />'

				output += '<h2>Have a new restaurant? </h2>'
				output += 'Add it <a href=\'/restaurant/register\'>here</a>!'
				output += "</body></html>"

				self.wfile.write(output.encode('utf=8'))
				print(output)

				return

			if self.path.endswith("/restaurant/register"):
				self.send_response(200)
				self.send_header('Content-type','text/html')
				self.end_headers()

				output = ""
				output += "<html><body>"
				output += "<h1>Register a new restaurant!</h1>"
				output += "<br />"
				output += """
				<form method='POST' enctype='multipart/form-data' action='/restaurant/register'>
				<input name='restaurant_name' type='text'>
				<input type='submit' value='Submit'>
				</form>
				"""

				output += "</body></html>"

				self.wfile.write(output.encode('utf-8'))
				print(output)
				return

			if self.path.endswith("/update"):
				restaurant_id_path = self.path.split("/")[2]
				data = session.query(Restaurant).filter_by(
					id=restaurant_id_path
					).one()

				self.send_response(200)
				self.send_header('Content-type','text/html')
				self.end_headers()


				output = ""
				output += "<html><body>"
				output += "<h1>Wanna rename this restaurant?</h1>"
				output += "<br />"

				output += """
				<form method='POST' enctype='multipart/form-data' action='/restaurant/{}/update'>
				<input name='new_restaurant_name' type='text' placeholder='{}'>
				<input type='submit' value='Submit'>
				</form>
				""".format(str(data.id), data.name)

				output += "</body></html>"

				self.wfile.write(output.encode('utf-8'))
				print(output)
				return

			if self.path.endswith("/delete"):
				restaurant_id_path = self.path.split("/")[2]
				data = session.query(Restaurant).filter_by(
					id=restaurant_id_path
					).one()

				self.send_response(200)
				self.send_header('Content-type','text/html')
				self.end_headers()

				output = ""
				output += "<html><body>"
				output += "<h1>Are you sure you wanna delete <i>{}</i> from restaurant list?</h1>".format(data.name)
				output += """
				<form method='POST' enctype='multipart/form-data' action='/restaurant/{}/delete'>
				<input type='submit' value='Delete'>
				</form>
				""".format(restaurant_id_path)

				output += "</body></html>"

				self.wfile.write(output.encode('utf-8'))
				print(output)
				
				return

		except IOError:
			self.send_error(404, "File not found: {}".format(self.path))

	def do_POST(self):
		try:
			if self.path.endswith("/register"):
				self.send_response(301)
				self.send_header('Content-type','text/html')
				self.end_headers()

				ctype, pdict = cgi.parse_header(self.headers['content-type'])
				pdict['boundary'] = bytes(pdict['boundary'], 'utf-8')

				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					message_content = fields.get('restaurant_name')

				new_record = Restaurant(name=message_content[0].decode())
				session.add(new_record)
				session.commit()

				output = ""
				output += "<html><body>"
				
				output += "<b>{} is successfully added!</b>".format(message_content[0].decode())
				output += "<br />"
				output += "Go back and verify it on <a href='/restaurant'>restaurant list!</a>"

				output += "</body></html>"
				self.wfile.write(output.encode('utf-8'))
				print(output)

			if self.path.endswith("/update"):
				self.send_response(301)
				self.send_header('Content-type','text/html')
				# self.send_header('Location','/restaurant')
				self.end_headers()

				ctype, pdict = cgi.parse_header(self.headers['content-type'])
				pdict['boundary'] = bytes(pdict['boundary'], 'utf-8')

				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					message_content = fields.get('new_restaurant_name')
					restaurant_id_path = self.path.split("/")[2]

				data = session.query(Restaurant).filter_by(id=restaurant_id_path).one()
				if data != []:
					previous_name = data.name
					data.name = message_content[0].decode()
					session.add(data)
					session.commit()

				output = ""
				output += "<html><body>"
				
				output += "<b>{} is successfully renamed to {}!</b>".format(previous_name, data.name)
				output += "<br />"
				output += "Go back and verify it on <a href='/restaurant'>restaurant list!</a>"

				output += "</body></html>"
				self.wfile.write(output.encode('utf-8'))
				print(output)

			if self.path.endswith("/delete"):
				self.send_response(301)
				self.send_header('Content-type','text/html')
				self.end_headers()

				ctype, pdict = cgi.parse_header(self.headers['content-type'])
				pdict['boundary'] = bytes(pdict['boundary'], 'utf-8')

				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					restaurant_id_path = self.path.split("/")[2]

				data = session.query(Restaurant).filter_by(id=restaurant_id_path).one()
				if data != []:
					deleted_restaurant_name = data.name
					session.delete(data)
					session.commit()

					output = ""
					output += "<html><body>"

					output += "{} is successfully deleted.".format(deleted_restaurant_name.encode('utf-8'))
					output += "<br />"
					output += "Go back and verify it on <a href='/restaurant'>restaurant list!</a>"

					output += "</body></html>"
					self.wfile.write(output.encode('utf-8'))
					print(output)


		except:
			pass


def main():
	try:
		port = 8081
		server = HTTPServer(('', port), WebServerHandler)
		print("Web server is running on port {}".format(port))
		server.serve_forever()

	except KeyboardInterrupt:
		print("^C entered, stopping web server...")
		server.socket.close()

if __name__ == '__main__':
	main()