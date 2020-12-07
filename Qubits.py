{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "name": "QuantumLib.ipynb",
      "provenance": [],
      "collapsed_sections": [],
      "authorship_tag": "ABX9TyOhEy0pE8DDSAXGIYgFjJGU",
      "include_colab_link": true
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
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
        "<a href=\"https://colab.research.google.com/github/franklinscudder/QuBits/blob/Development/Qubits.py\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
      ]
    },
    {
      "cell_type": "code",
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/"
        },
        "id": "Nj4_GTQ1Ezbs",
        "outputId": "5123f280-f891-4cb4-b29c-3250650d0ec2"
      },
      "source": [
        "import numpy as np\n",
        "import scipy.linalg as sp\n",
        "import random\n",
        "\n",
        "class register:\n",
        "    \"\"\" An N-bit quantum register object, with 2^N states. \"\"\"\n",
        "    def __init__(self, NBits):\n",
        "        checkNBits(NBits)\n",
        "        self.NBits = NBits\n",
        "        self.NStates = 2 ** NBits\n",
        "        self.amps = np.zeros(self.NStates, dtype=np.dtype(complex))\n",
        "        self.amps[0] = 1 + 0j\n",
        "    \n",
        "    def probabilites(self):\n",
        "        \"\"\" Returns the probability associated with observing each state. \"\"\"\n",
        "        return np.array([abs(i)**2 for i in self.amps])\n",
        "    \n",
        "    def observe(self):\n",
        "        \"\"\" 'Observes' the register and returns an integer representation of the observed state according to the probability amplitudes. \"\"\"\n",
        "        probs = self.probabilites()\n",
        "        return random.choices(range(self.NStates), probs)\n",
        "    \n",
        "    def __str__(self):\n",
        "        stri = \"\"\n",
        "        for state, amp in enumerate(self.amps):\n",
        "            stri = stri + f' {amp:.3f}'.rjust(15) + \" |\" + str(state).ljust(2) + \"> +\\r\\n\"\n",
        "        return stri.rstrip(\"+\\r\\n\")\n",
        "    \n",
        "    def prod(self, B):\n",
        "        \"\"\" Returns the tensor product of self and B, 'Joining' two registers into a single larger register with self at the MSB and B at the LSB. \"\"\"\n",
        "        result = register(self.NBits + B.NBits)\n",
        "        result.amps = np.kron(self.amps, B.amps)    ### Needs more testing\n",
        "        return result\n",
        "    \n",
        "\n",
        "class genericGate:\n",
        "    \"\"\" A base class for callable quantum logic gates. \"\"\"\n",
        "    def __init__(self, NBits):\n",
        "        checkNBits(NBits)\n",
        "        self.NBits = NBits\n",
        "        self.matrix = np.identity(2 ** NBits)\n",
        "    \n",
        "    def __call__(self, arg):\n",
        "        if issubclass(type(arg), genericGate):\n",
        "            out = genericGate(self.NBits + arg.NBits)\n",
        "            out.matrix = np.matmul(self.matrix, arg.matrix)\n",
        "            return out\n",
        "\n",
        "        elif type(arg) == register:\n",
        "            result = register(arg.NBits)\n",
        "            result.amps = np.matmul(self.matrix, arg.matrix)\n",
        "            return result\n",
        "        \n",
        "        else:\n",
        "            raise TypeError(\"Gates can only be called on gates or registers! Got type: \" +  str(type(arg)))\n",
        "    \n",
        "    def __str__(self):\n",
        "        stri = str(self.NBits) + \"-bit \" + type(self).__name__ + \" Gate, Matrix:\\n\\r\"\n",
        "        stri = stri + self.matrix.__str__()\n",
        "        return stri\n",
        "\n",
        "class hadamard(genericGate):\n",
        "    \"\"\" Creates a callable hadamard gate object \"\"\"\n",
        "    def __init__(self, NBits):\n",
        "        super(hadamard, self).__init__(NBits)\n",
        "        self.matrix = sp.hadamard(2 ** NBits) * (2**(-0.5*(NBits)))\n",
        "\n",
        "class phaseShift(genericGate):\n",
        "    \"\"\" Creates a callable phase-shift gate object \"\"\"\n",
        "    def __init__(self, NBits, phi):\n",
        "        super(phaseShift, self).__init__(NBits)\n",
        "        singleMatrix = np.array([[1,0],[0,np.exp(phi * 1j)]])\n",
        "        self.matrix = toNBitMatrix(singleMatrix, NBits)\n",
        "\n",
        "class pauliX(genericGate):\n",
        "    \"\"\" Creates a callable Pauli-X gate object \"\"\"\n",
        "    def __init__(self, NBits):\n",
        "        super(pauliX, self).__init__(NBits)\n",
        "        singleMatrix = np.array([[0,1],[1,0]])    \n",
        "        self.matrix = toNBitMatrix(singleMatrix, NBits)\n",
        "\n",
        "class pauliY(genericGate):\n",
        "    \"\"\" Creates a callable Pauli-Y gate object \"\"\"\n",
        "    def __init__(self, NBits):\n",
        "        super(pauliY, self).__init__(NBits)\n",
        "        singleMatrix = np.array([[0,-1j],[1j,0]])    \n",
        "        self.matrix = toNBitMatrix(singleMatrix, NBits) \n",
        "\n",
        "class pauliZ(phaseShift):\n",
        "    \"\"\" Creates a callable Pauli-Z gate object \"\"\"\n",
        "    def __init__(self, NBits):\n",
        "        super(pauliZ, self).__init__(NBits, np.pi)\n",
        "\n",
        "class cNot(genericGate):\n",
        "    \"\"\" Creates Controlled-Not gate object (first bit is the control bit) \"\"\"\n",
        "    def __init__(self):\n",
        "        super(cNot, self).__init__(2)   \n",
        "        self.matrix = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]])\n",
        "\n",
        "def checkNBits(NBits):\n",
        "    if NBits < 1:\n",
        "        raise ValueError(\"NBits must be a positive integer!\")\n",
        "    \n",
        "    if type(NBits) != int:\n",
        "        raise TypeError(\"NBits must be a positive integer!\")\n",
        "    \n",
        "\n",
        "\n",
        "def prod(regA, regB):\n",
        "    \"\"\" Joins two registers into a single larger register with regA at the MSB and regB at the LSB. \"\"\"\n",
        "    result = register(regA.NBits + regB.NBits)\n",
        "    result.amps = np.kron(regA.amps, regB.amps)    ### Needs more testing\n",
        "    return result\n",
        "\n",
        "def toNBitMatrix(m, NBits):\n",
        "    \"\"\" Takes a single-bit matrix of a gate and returns the NBit equivalent matrix \"\"\"\n",
        "    m0 = m\n",
        "    mOut = m\n",
        "    for i in range(NBits - 1):\n",
        "        mOut = np.kron(mOut, m0)\n",
        "    \n",
        "    return mOut\n",
        "\n",
        "if __name__ == \"__main__\":\n",
        "    h = hadamard(2)\n",
        "    c = cNot()\n",
        "    p = pauliY(2)\n",
        "\n",
        "    print(h)\n",
        "    print(c(h))\n",
        "    print(p(c(h)))\n"
      ],
      "execution_count": 19,
      "outputs": [
        {
          "output_type": "stream",
          "text": [
            "2-bit hadamard Gate, Matrix:\n",
            "\r[[ 0.5  0.5  0.5  0.5]\n",
            " [ 0.5 -0.5  0.5 -0.5]\n",
            " [ 0.5  0.5 -0.5 -0.5]\n",
            " [ 0.5 -0.5 -0.5  0.5]]\n",
            "4-bit genericGate Gate, Matrix:\n",
            "\r[[ 0.5  0.5  0.5  0.5]\n",
            " [ 0.5 -0.5  0.5 -0.5]\n",
            " [ 0.5 -0.5 -0.5  0.5]\n",
            " [ 0.5  0.5 -0.5 -0.5]]\n",
            "6-bit genericGate Gate, Matrix:\n",
            "\r[[-0.5+0.j -0.5+0.j  0.5+0.j  0.5+0.j]\n",
            " [ 0.5+0.j -0.5+0.j -0.5+0.j  0.5+0.j]\n",
            " [ 0.5+0.j -0.5+0.j  0.5+0.j -0.5+0.j]\n",
            " [-0.5+0.j -0.5+0.j -0.5+0.j -0.5+0.j]]\n"
          ],
          "name": "stdout"
        }
      ]
    }
  ]
}