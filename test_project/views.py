from django import http

def default(request):
    return http.HttpResponse("""<html>
    <body>
    <h1>It works!</h1>
    </body>
</html>""")
