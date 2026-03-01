from scripts.load_private_data import load_private_data
from scripts.scrape import extract_website_from_md
from scripts.scrape import scrape_public_data
from scripts.generate_text import generate_slide_text
from scripts.anonymize import check_anonymization
from scripts.generate_ppt import create_ppt
from scripts.citations import create_citations
import json
import os


def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def select_company(companies):
    print("\n" + "="*50)
    print("COMPANY TEASER DECK GENERATOR")
    print("="*50)
    print("\nAvailable Companies:\n")
    
    for idx, company in enumerate(companies, 1):
        print(f"  {idx}. {company['name']}")
    
    print(f"  {len(companies) + 1}. Enter custom file path")
    print("\n" + "="*50)
    
    while True:
        try:
            choice = input("\nSelect company number: ").strip()
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(companies):
                return companies[choice_num - 1]
            elif choice_num == len(companies) + 1:
                custom_file = input("Enter the .md file name: ").strip()
                custom_name = input("Enter company name: ").strip()
                return {"name": custom_name, "file": custom_file}
            else:
                print(f"Please enter a number between 1 and {len(companies) + 1}")
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            exit(0)


def main():
    # Load configuration
    config = load_config()
    companies = config["companies"]
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, config["data_directory"])
    
    # Let user select company
    selected = select_company(companies)
    
    # Build file path
    FILE_TO_READ = os.path.join(data_dir, selected["file"])
    
    # Verify file exists
    if not os.path.exists(FILE_TO_READ):
        print(f"\n Error: File not found: {FILE_TO_READ}")
        return
    
    print(f"\n✓ Selected: {selected['name']}")
    print(f"✓ File: {FILE_TO_READ}\n")
    # Load API Key
    api_key = config.get("api_key")
    if not api_key:
        print("\n Error: 'api_key' not found in config.json")
        return

    print("="*50)

    print("\n[1/6] Loading private data...")
    private_data = load_private_data(FILE_TO_READ)
    
    with open(FILE_TO_READ, "r", encoding="utf-8") as f:
        md_text = f.read()

    print("[2/6] Extracting website URL from MD...")
    base_url = extract_website_from_md(md_text)

    print("[3/6] Scraping public data from website...")
    public_data = scrape_public_data(base_url)

    print("[4/6] Generating slide text using AI...")
    slide_text = generate_slide_text(private_data, public_data, api_key)

    print("[5/6] Checking anonymization...")
    slide_text = check_anonymization(slide_text)

    print("[6/6] Creating PowerPoint presentation...")
    create_ppt(slide_text)

    print("\n[Bonus] Creating citations document...")
 
    # Add AI-generated citations to the data passed to the citation generator
    if "citations" in slide_text:
        public_data["citations"] = slide_text["citations"]
        
    create_citations(private_data, public_data)

    print("\n" + "="*50)
    print("COMPLETED SUCCESSFULLY")
    print("="*50)


if __name__ == "__main__":
    main()