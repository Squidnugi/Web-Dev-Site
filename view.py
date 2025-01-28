class WebView():
    def show(self, data):
        if data:
            page = 'in-home.html'
        else:
            page = 'out-home.html'
        return page
