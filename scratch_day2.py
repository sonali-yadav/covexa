from core import llm


file_id = llm.upload("samples/motor_policy.pdf")
# response = llm.ask_about_file(file_id=file_id, 
#                    question="What is the deductible?", 
#                    model=llm.MODEL_FAST, max_tokens=1024)

response = llm.ask_about_file(file_id=file_id, 
                   question="Does this policy cover heart attacks?", 
                   model=llm.MODEL_FAST, max_tokens=1024)


print(response.text)
print("stop_reason:", response.stop_reason)
print("input_tokens:", response.input_tokens)
print("output_tokens:", response.output_tokens)