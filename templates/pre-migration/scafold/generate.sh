
export TEXMFHOME="{{ TEXMF_PATH }}"

pushd {{ ROOT_PATH }} > /dev/null

echo "==============================" && pdflatex scafold/pre-migration-{{airline}} && \
echo "==============================" && pdflatex scafold/pre-migration-{{airline}} && \
echo "==============================" && pdflatex scafold/pre-migration-{{airline}}

popd > /dev/null
