class Hsg < Formula
  desc "Chinese text coverage analysis and comprehensible sentence mining"
  homepage "https://github.com/deedeedev/hsg"
  url "https://github.com/deedeedev/hsg/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "8d0c4fb08b8b70369ddab931716343db0f30d631e291cf2292fe76918da90274"
  license "Apache-2.0"

  depends_on "python@3.12"

  def install
    python = Formula["python@3.12"].opt_bin/"python3.12"
    system python, "-m", "venv", libexec
    system libexec/"bin/pip", "install", "--upgrade", "pip"
    system libexec/"bin/pip", "install", "."
    bin.install_symlink libexec/"bin/hsg"
  end

  test do
    system bin/"hsg", "--help"
  end
end
