class Hsg < Formula
  desc "Chinese text coverage analysis and comprehensible sentence mining"
  homepage "https://github.com/davide/hsg"
  url "https://github.com/davide/hsg/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "REPLACE_WITH_ACTUAL_SHA256"
  license "Apache-2.0"

  depends_on "python@3.12"

  def install
    system "pipx", "install", "--python", Formula["python@3.12"].opt_bin/"python3.12", "."
    bin.install Dir["#{libexec}/bin/*"]
  end

  test do
    system "#{bin}/hsg", "--help"
  end
end
