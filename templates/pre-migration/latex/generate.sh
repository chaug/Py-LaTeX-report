export TEXMFHOME="{{ TEXMF_PATH }}"

pushd {{ DOCUMENT_PATH }} > /dev/null

echo "==============================" && pdflatex pre-migration-{{airline}} && \
echo "==============================" && pdflatex pre-migration-{{airline}} && \
echo "==============================" && pdflatex pre-migration-{{airline}}

popd > /dev/null
