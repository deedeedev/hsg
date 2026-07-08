class Hsg < Formula
  include Language::Python::Virtualenv

  desc "Chinese text coverage analysis and comprehensible sentence mining"
  homepage "https://github.com/deedeedev/hsg"
  url "https://github.com/deedeedev/hsg/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "826fab34bc560a43850666e9da10fd1ed55d2aaabbf9c9c9c803a4cd06a60751"
  license "Apache-2.0"

  depends_on "python@3.12"

  def install
    virtualenv_install
  end

  test do
    system bin/"hsg", "--help"
  end
end
