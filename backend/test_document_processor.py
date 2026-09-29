from document_processor import process_document


file_path = "data/graphrag/employees/Alice_profile.txt"

result = process_document(file_path)

print("\nFILE:")
print(result["file_name"])

print("\nNUMBER OF CHUNKS:")
print(len(result["chunks"]))

print("\nFIRST CHUNK:")
print(result["chunks"][0])

print("\nEMBEDDING SIZE:")
print(len(result["embeddings"][0]))

print("\nFIRST 10 EMBEDDING VALUES:")
print(result["embeddings"][0][:10])