{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "provenance": [],
      "authorship_tag": "ABX9TyOUALxuyZ7JCa6cd7emMz4E",
      "include_colab_link": true
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
    }
  },
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "view-in-github",
        "colab_type": "text"
      },
      "source": [
        "<a href=\"https://colab.research.google.com/github/marclagler/MDPI-Project/blob/main/main.py\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "collapsed": true,
        "id": "zkKf_LXkKRCK"
      },
      "outputs": [],
      "source": [
        "!pip install fastapi uvicorn transformers sentence-transformers ngrok poetry"
      ]
    },
    {
      "cell_type": "markdown",
      "source": [
        "Load Pre-Trained NLP Model from HuggingFace"
      ],
      "metadata": {
        "id": "vrf-13j_kjMz"
      }
    },
    {
      "cell_type": "code",
      "source": [
        "from sentence_transformers import SentenceTransformer\n",
        "import numpy as np\n",
        "\n",
        "# Load a pre-trained sentence embedding model\n",
        "model = SentenceTransformer('all-MiniLM-L6-v2')\n",
        "\n",
        "# Example usage\n",
        "sentences = [\"Higgs boson in particle physics\", \"Particle physics at CERN\"]\n",
        "embeddings = model.encode(sentences)\n",
        "\n",
        "# Check similarity using cosine similarity\n",
        "cosine_similarity = np.dot(embeddings[0], embeddings[1]) / (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1]))\n",
        "print(\"Cosine Similarity:\", cosine_similarity)"
      ],
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/"
        },
        "collapsed": true,
        "id": "tm8w9RF2ghR4",
        "outputId": "3842550b-f93d-487a-cd10-742c50111d6b"
      },
      "execution_count": 2,
      "outputs": [
        {
          "output_type": "stream",
          "name": "stderr",
          "text": [
            "/usr/local/lib/python3.11/dist-packages/huggingface_hub/utils/_auth.py:94: UserWarning: \n",
            "The secret `HF_TOKEN` does not exist in your Colab secrets.\n",
            "To authenticate with the Hugging Face Hub, create a token in your settings tab (https://huggingface.co/settings/tokens), set it as secret in your Google Colab and restart your session.\n",
            "You will be able to reuse this secret in all of your notebooks.\n",
            "Please note that authentication is recommended but still optional to access public models or datasets.\n",
            "  warnings.warn(\n"
          ]
        },
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            "Cosine Similarity: 0.5001519\n"
          ]
        }
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "from fastapi import FastAPI\n",
        "from pydantic import BaseModel\n",
        "import numpy as np\n",
        "from sentence_transformers import SentenceTransformer\n",
        "\n",
        "app = FastAPI()\n",
        "model = SentenceTransformer('all-MiniLM-L6-v2')\n",
        "\n",
        "class TitleRequest(BaseModel):\n",
        "    reference: str\n",
        "    other: list[str]\n",
        "\n",
        "@app.post(\"/find_most_similar/\")\n",
        "async def find_most_similar(request: TitleRequest):\n",
        "    reference_embedding = model.encode([request.reference])[0]\n",
        "    other_embeddings = model.encode(request.other)\n",
        "\n",
        "    similarities = [np.dot(reference_embedding, other) /\n",
        "                    (np.linalg.norm(reference_embedding) * np.linalg.norm(other))\n",
        "                    for other in other_embeddings]\n",
        "\n",
        "    best_match_index = np.argmax(similarities)\n",
        "    return {\"top_result\": request.other[best_match_index]}\n"
      ],
      "metadata": {
        "id": "kLXMbXfAg_2g"
      },
      "execution_count": 4,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "from pyngrok import ngrok\n",
        "import uvicorn\n",
        "import threading\n",
        "\n",
        "# Run FastAPI using Uvicorn\n",
        "def run():\n",
        "    uvicorn.run(app, host=\"0.0.0.0\", port=8000)\n",
        "\n",
        "thread = threading.Thread(target=run)\n",
        "thread.start()\n",
        "\n",
        "# Expose the API publicly\n",
        "public_url = ngrok.connect(8000).public_url\n",
        "print(\"Public URL:\", public_url)"
      ],
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/"
        },
        "id": "x7ofM6KbhRdj",
        "outputId": "fa6449d6-4651-412b-9dfd-f3d3fb9ae251"
      },
      "execution_count": 5,
      "outputs": [
        {
          "output_type": "stream",
          "name": "stderr",
          "text": [
            "INFO:     Started server process [22629]\n",
            "INFO:     Waiting for application startup.\n",
            "INFO:     Application startup complete.\n",
            "INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)\n"
          ]
        },
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            "Public URL: https://af2b-35-243-244-212.ngrok-free.app\n"
          ]
        }
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "import requests\n",
        "\n",
        "url = \"PASTE_PUBLIC_URL_HERE/find_most_similar/\"\n",
        "data = {\n",
        "    \"reference\": \"Higgs boson in particle physics\",\n",
        "    \"other\": [\"Best soup recipes\", \"Basel activities\", \"Particle physics at CERN\"]\n",
        "}\n",
        "\n",
        "response = requests.post(url, json=data)\n",
        "print(response.json())"
      ],
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/",
          "height": 436
        },
        "collapsed": true,
        "id": "8EpchgJ0iTDM",
        "outputId": "bd1e1471-c1fa-4a7f-8a31-83cd97720e16"
      },
      "execution_count": 6,
      "outputs": [
        {
          "output_type": "error",
          "ename": "MissingSchema",
          "evalue": "Invalid URL 'PASTE_PUBLIC_URL_HERE/find_most_similar/': No scheme supplied. Perhaps you meant https://PASTE_PUBLIC_URL_HERE/find_most_similar/?",
          "traceback": [
            "\u001b[0;31m---------------------------------------------------------------------------\u001b[0m",
            "\u001b[0;31mMissingSchema\u001b[0m                             Traceback (most recent call last)",
            "\u001b[0;32m<ipython-input-6-ca6ee44cbd9d>\u001b[0m in \u001b[0;36m<cell line: 0>\u001b[0;34m()\u001b[0m\n\u001b[1;32m      7\u001b[0m }\n\u001b[1;32m      8\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m----> 9\u001b[0;31m \u001b[0mresponse\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mrequests\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mpost\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0murl\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mjson\u001b[0m\u001b[0;34m=\u001b[0m\u001b[0mdata\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m     10\u001b[0m \u001b[0mprint\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mresponse\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mjson\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n",
            "\u001b[0;32m/usr/local/lib/python3.11/dist-packages/requests/api.py\u001b[0m in \u001b[0;36mpost\u001b[0;34m(url, data, json, **kwargs)\u001b[0m\n\u001b[1;32m    113\u001b[0m     \"\"\"\n\u001b[1;32m    114\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m--> 115\u001b[0;31m     \u001b[0;32mreturn\u001b[0m \u001b[0mrequest\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0;34m\"post\"\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0murl\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mdata\u001b[0m\u001b[0;34m=\u001b[0m\u001b[0mdata\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mjson\u001b[0m\u001b[0;34m=\u001b[0m\u001b[0mjson\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0;34m**\u001b[0m\u001b[0mkwargs\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m    116\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m    117\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n",
            "\u001b[0;32m/usr/local/lib/python3.11/dist-packages/requests/api.py\u001b[0m in \u001b[0;36mrequest\u001b[0;34m(method, url, **kwargs)\u001b[0m\n\u001b[1;32m     57\u001b[0m     \u001b[0;31m# cases, and look like a memory leak in others.\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m     58\u001b[0m     \u001b[0;32mwith\u001b[0m \u001b[0msessions\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mSession\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0;34m)\u001b[0m \u001b[0;32mas\u001b[0m \u001b[0msession\u001b[0m\u001b[0;34m:\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m---> 59\u001b[0;31m         \u001b[0;32mreturn\u001b[0m \u001b[0msession\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mrequest\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mmethod\u001b[0m\u001b[0;34m=\u001b[0m\u001b[0mmethod\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0murl\u001b[0m\u001b[0;34m=\u001b[0m\u001b[0murl\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0;34m**\u001b[0m\u001b[0mkwargs\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m     60\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m     61\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n",
            "\u001b[0;32m/usr/local/lib/python3.11/dist-packages/requests/sessions.py\u001b[0m in \u001b[0;36mrequest\u001b[0;34m(self, method, url, params, data, headers, cookies, files, auth, timeout, allow_redirects, proxies, hooks, stream, verify, cert, json)\u001b[0m\n\u001b[1;32m    573\u001b[0m             \u001b[0mhooks\u001b[0m\u001b[0;34m=\u001b[0m\u001b[0mhooks\u001b[0m\u001b[0;34m,\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m    574\u001b[0m         )\n\u001b[0;32m--> 575\u001b[0;31m         \u001b[0mprep\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mself\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mprepare_request\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mreq\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m    576\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m    577\u001b[0m         \u001b[0mproxies\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mproxies\u001b[0m \u001b[0;32mor\u001b[0m \u001b[0;34m{\u001b[0m\u001b[0;34m}\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n",
            "\u001b[0;32m/usr/local/lib/python3.11/dist-packages/requests/sessions.py\u001b[0m in \u001b[0;36mprepare_request\u001b[0;34m(self, request)\u001b[0m\n\u001b[1;32m    482\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m    483\u001b[0m         \u001b[0mp\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mPreparedRequest\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m--> 484\u001b[0;31m         p.prepare(\n\u001b[0m\u001b[1;32m    485\u001b[0m             \u001b[0mmethod\u001b[0m\u001b[0;34m=\u001b[0m\u001b[0mrequest\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mmethod\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mupper\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m,\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m    486\u001b[0m             \u001b[0murl\u001b[0m\u001b[0;34m=\u001b[0m\u001b[0mrequest\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0murl\u001b[0m\u001b[0;34m,\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n",
            "\u001b[0;32m/usr/local/lib/python3.11/dist-packages/requests/models.py\u001b[0m in \u001b[0;36mprepare\u001b[0;34m(self, method, url, headers, files, data, params, auth, cookies, hooks, json)\u001b[0m\n\u001b[1;32m    365\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m    366\u001b[0m         \u001b[0mself\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mprepare_method\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mmethod\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m--> 367\u001b[0;31m         \u001b[0mself\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mprepare_url\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0murl\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mparams\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m    368\u001b[0m         \u001b[0mself\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mprepare_headers\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mheaders\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m    369\u001b[0m         \u001b[0mself\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mprepare_cookies\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mcookies\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n",
            "\u001b[0;32m/usr/local/lib/python3.11/dist-packages/requests/models.py\u001b[0m in \u001b[0;36mprepare_url\u001b[0;34m(self, url, params)\u001b[0m\n\u001b[1;32m    436\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m    437\u001b[0m         \u001b[0;32mif\u001b[0m \u001b[0;32mnot\u001b[0m \u001b[0mscheme\u001b[0m\u001b[0;34m:\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m--> 438\u001b[0;31m             raise MissingSchema(\n\u001b[0m\u001b[1;32m    439\u001b[0m                 \u001b[0;34mf\"Invalid URL {url!r}: No scheme supplied. \"\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m    440\u001b[0m                 \u001b[0;34mf\"Perhaps you meant https://{url}?\"\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n",
            "\u001b[0;31mMissingSchema\u001b[0m: Invalid URL 'PASTE_PUBLIC_URL_HERE/find_most_similar/': No scheme supplied. Perhaps you meant https://PASTE_PUBLIC_URL_HERE/find_most_similar/?"
          ]
        }
      ]
    },
    {
      "cell_type": "markdown",
      "source": [],
      "metadata": {
        "id": "2M0rIxD0miLB"
      }
    },
    {
      "cell_type": "code",
      "source": [
        "#ngrok expires after some time (usually 2 hours for free accounts). If the tunnel stops working, run:\n",
        "public_url = ngrok.connect(8000).public_url\n",
        "print(\"New Public URL:\", public_url)"
      ],
      "metadata": {
        "id": "EQ3ZA_DUmg9q"
      },
      "execution_count": null,
      "outputs": []
    }
  ]
}