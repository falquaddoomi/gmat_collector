#!/bin/env python

from gmat_collector import app

# start the flask loop
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5580)
