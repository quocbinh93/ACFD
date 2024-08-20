import use_case_input
import cfd_generation
import test_case_generation
from fpdf import FPDF
import os

def create_pdf_with_test_paths(test_paths, filename="test_paths.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    for i, path in enumerate(test_paths, start=1):
        test_path_str = f"Test Path {i}: {', '.join(map(str, path))}"
        pdf.cell(200, 10, txt=test_path_str, ln=True, align='L')
    
    pdf.output(filename)
    print(f"PDF created: {filename}")

def main():
    # Run the Tkinter event loop to show the GUI and allow user input
    use_case_input.window.mainloop()

    # Now that the window is closed, retrieve the data from the global variable:
    use_case_data = use_case_input.use_case_data

    if use_case_data:  # Kiểm tra xem dữ liệu có được thu thập thành công không
        try:
            # Create control flow graph
            control_flow_graph = cfd_generation.acfd(use_case_data)

            # Generate and visualize test cases
            test_paths = cfd_generation.generate_test_paths(control_flow_graph)
            optimized_test_cases = test_case_generation.optimize_test_cases(test_paths, control_flow_graph)
            
            # Remove duplicate optimized test paths
            unique_optimized_test_cases = []
            seen = set()
            for path in optimized_test_cases:
                path_tuple = tuple(path)
                if path_tuple not in seen:
                    seen.add(path_tuple)
                    unique_optimized_test_cases.append(path)

            # Print all test paths to console
            print("All Test Paths:")
            for i, path in enumerate(test_paths, start=1):
                print(f"Test Path {i}: {', '.join(map(str, path))}")
            
            # Ensure output directory exists
            output_directory = "output"
            os.makedirs(output_directory, exist_ok=True)

            # Create PDF with test paths
            create_pdf_with_test_paths(test_paths, filename=os.path.join(output_directory, "test_paths.pdf"))

            # Print unique optimized test cases to console
            print("Unique Optimized Test Cases:")
            for i, path in enumerate(unique_optimized_test_cases, start=1):
                print(f"Optimized Test Path {i}: {', '.join(map(str, path))}")

            # Create PDF with unique optimized test paths
            create_pdf_with_test_paths(unique_optimized_test_cases, filename=os.path.join(output_directory, "test_paths_optimized.pdf"))

            # Visualize control flow graph with unique optimized test cases
            for i, test_case in enumerate(unique_optimized_test_cases):
                cfd_generation.visualize_control_flow_graph(control_flow_graph, test_case, i + 1)

            # Visualize control flow graph
            cfd_generation.visualize_control_flow_graph(control_flow_graph)
        
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print("Không có dữ liệu use case được nhập.")

if __name__ == "__main__":
    main()