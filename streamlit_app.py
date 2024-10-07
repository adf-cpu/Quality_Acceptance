import streamlit as st
import pandas as pd
from datetime import datetime
import random
import cloudinary
import cloudinary.uploader
import os

# Use Streamlit's image function to show the image on the left side
col1, col2 = st.columns([1, 3])  # Create 2 columns with ratios (left narrower than right)

with col1:  # Left column
    st.image("Huawei.jpg", width=80)

cloudinary.config(
    cloud_name="drpkmvcdb",  # Replace with your Cloudinary cloud name
    api_key="421723639371647",        # Replace with your Cloudinary API key
    api_secret="AWpJzomMBrw-5DHNqujft5scUbM"   # Replace with your Cloudinary API secret
)

def upload_to_cloudinary(file_path, public_id):
    try:
        response = cloudinary.uploader.upload(
            file_path,
            resource_type="raw",
            public_id=public_id,
            overwrite=True,  # Allow overwriting
            invalidate=True,  # Invalidate cached versions on CDN
            unique_filename=False,  # Do not generate a unique filename
            use_filename=True  # Use the file's original filename
        )
        return response['secure_url']
    except cloudinary.exceptions.Error as e:
        st.error(f"Cloudinary upload failed: {str(e)}")
        return None

# Function to save quiz results to Excel and upload to Cloudinary
def save_results(username, total_attempted, correct_answers, wrong_answers, total_score, time_taken, details):
    try:
        df = pd.read_excel("quiz_results_qa.xlsx")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Username", "Date", "Total Attempted", "Correct Answers", "Wrong Answers", "Total Score", "Time Taken", "Details"])

    new_data = pd.DataFrame([[username, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), total_attempted, correct_answers, wrong_answers, total_score, time_taken, details]],
                            columns=["Username", "Date", "Total Attempted", "Correct Answers", "Wrong Answers", "Total Score", "Time Taken", "Details"])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_excel("quiz_results_qa.xlsx", index=False)

    # Upload the file to Cloudinary
    uploaded_url = upload_to_cloudinary("quiz_results_qa.xlsx", "quiz_results_qa")
    if uploaded_url:
        st.success("Quiz results uploaded successfully!")
        # st.markdown(f"Access your file here: [quiz_results.xlsx]({uploaded_url})")

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'answers' not in st.session_state:
    st.session_state.answers = []
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'quiz_submitted' not in st.session_state:
    st.session_state.quiz_submitted = False
if 'flattened_questions' not in st.session_state:
    st.session_state.flattened_questions = []
# List of allowed usernames
allowed_usernames = {
    "safaa_asadmurad",
    "safaa_ashfaq",
    "nk_adnanali12",
    "nk_waseem11",
    "ies_zaheer03",
    "ies_hamzashafique",
    "safaa_mansar"
}
# Define your questions
QAC = {
    "true_false": [
        {"question": "When the outdoor feeders enter the indoor system, they need to be connected to the surge protector to protect the BTS equipment against damages from lightning.", "answer": "False"},
        {"question": "According to radiation direction, the antenna can be classified into omni directional antenna and directional antenna.", "answer": "True"},
        {"question": "The level-2 VSWR alarm will cause a serious consequence, therefore, it is better to set the level-2 VSWR threshold lower than 2.0.", "answer": "True"},
        {"question": "Jumper is quite soft, its common specification is 1/2” and can be used for long distance connection.", "answer": "False"},
        {"question": "When installed on a tower, only one RRU can be installed in standard mode or reverse mode, and two RRUs can be installed on a pole in back-to-back mode. RRUs cannot be installed on the side, and the brackets for more than two RRUs cannot be combined.", "answer": "False"},
        {"question": "The labels of communication cables, feeder cables and jumper should be stuck and tied according to specifications. The labels should be arranged in an orderly way with same direction.", "answer": "True"},
        {"question": "The jumper of the antenna should be tied along the rail of the support to the steel frame of the power.", "answer": "True"},
        {"question": "The black cable tie used for outdoor cable colligation and fixation normally.", "answer": "True"},
        {"question": "The feeder cable's bending radius should be more than ten times of the cable's diameter.", "answer": "True"},
        {"question": "Electrical tilt antenna has remote control function, can control the downtilt angle, azimuth angle remotely.", "answer": "False"},
        {"question": "3～5mm should left When cut off the surplus binding strap to resist expansion and contraction.", "answer": "True"},
        {"question": "BBU3900 can be installed in the 19-Inch’s cabinet.", "answer": "True"},
        {"question": "It’s necessary to make a drip-loop before the cable entering the feeder window, and the entrance of the feeder-window must be waterproofed.", "answer": "True"},
        {"question": "It’s forbidden to look at the laser directly, also the laser shouldn’t be directed at eyes.", "answer": "True"},
        {"question": "The Electronic Serial Number (ESN) is not a unique identifier of a Network Element(NE). Record the ESN for later commissioning of the base station before installation.", "answer": "False"},
        {"question": "When you connect RFUs to ISM6 boards, it is recommended that you connect RFUs in the same polarization direction to ISM6 board ports of the same ID. For example, connect RFUs in the vertical polarization direction to ISM6 board ports whose IDs are 1, and connect RFUs in the horizontal polarization direction to ISM6 board ports whose IDs are 2.", "answer": "True"},
        {"question": "Exposed live parts such as diesel generator, transformer and distribution cabinet shall be insulated or isolated, and the electric shock hazard sign shall be posted.", "answer": "True"},
        {"question": "As shown in the following photo, the clearance after site construction is complete meets the quality requirements.", "answer": "False"},
        {"question": "The power cable and grounding cable must be made of copper core materials, and there can be connectors in the middle.", "answer": "True"},
        {"question": "Huawei microwave IDIJ supports two power supply voltages: -48 V DC and -60 V DC. The allowed voltage ranges from -38.4 V DC to -72 V DC.", "answer": "True"},
        {"question": "Two ground cables can be connected to the same grounding hole on grounding busbar.", "answer": "False"},
        {"question": "The bolt installed in the following photo are correct.", "answer": "False"},
        {"question": "The vertical deviation of cabinets and the clearance between combined cabinets should be less than 3 mm. The cabinets in each row along the main aisle should be in a straight line with the deviation less than 5 mm.", "answer": "True"},
        {"question": "Keep at least 10 mm spacing between storage batteries to facilitate heat dissipation during storage battery operation.", "answer": "True"},
        {"question": "Adding a Female Fast Connector (Screw-free Type) to the RRU Power Cable on the RRU Side, the stripped length of the power cable must be greater than or equal to 18 mm, each core wire must be exposed outside the female fast connector (screw-free type) (ensure that the exposed part is not excessively long), and the connector must not press the outer insulation layer of the power cable.", "answer": "True"},
        {"question": "Route the RRU power cable from the RRU side to the power equipment side through the feeder window. Install a ground clip near the feeder window outside the equipment room, Wrap three layers of waterproof tape and three layers of insulation tape around the ground clip. And connect the PGND cable on the ground clip to the external ground bar.", "answer": "True"},
        {"question": "After the ODIJ is unpacked, it must be powered on within 24 hours to avoid moisture accumulation in it.", "answer": "True"},
    ],
    "choose_correct": [
        {
            "question": "What are the impacts of level-1 VSWR alarm?",
            "options": ["A) Service interrupt", "B) The RF emissive power reduces", "C) The amplifier of RF unit is shut down", "D) Shrink the cell coverage"],
            "answer": ["B) The RF emissive power reduces", "D) Shrink the cell coverage"]  # Correct answers
        },
        {
        "question": "What are the impacts of level-1 VSWR alarm?",
        "options": [
            "A) Service interrupt",
            "B) The RF emissive power reduces",
            "C) The amplifier of RF unit is shut down",
            "D) Shrink the cell coverage"
        ],
        "answer": ["B) The RF emissive power reduces", "D) Shrink the cell coverage"]
    },
    {
        "question": "Which type of the transmission can be supported by WMPT board?",
        "options": [
            "A) E1/T1",
            "B) Electronic IP",
            "C) Optical IP",
            "D) Microwave"
        ],
        "answer": ["A) E1/T1", "B) Electronic IP", "C) Optical IP"]
    },
    {
        "question": "BBU3900’s functions include",
        "options": [
            "A) interactive communication between BTS and BSC",
            "B) provide the system clock",
            "C) BTS Centralized Management",
            "D) provide the maintenance channel with LMT(or M2000)"
        ],
        "answer": ["A) interactive communication between BTS and BSC", "B) provide the system clock", "C) BTS Centralized Management", "D) provide the maintenance channel with LMT(or M2000)"]
    },
    {
        "question": "Option board of BBU3900 includes",
        "options": [
            "A) power module UPEU",
            "B) E1 surge protector UELP",
            "C) Universal clock unit USCU",
            "D) Environment monitor interface board UEIU"
        ],
        "answer": ["B) E1 surge protector UELP", "C) Universal clock unit USCU", "D) Environment monitor interface board UEIU"]
    },
    {
        "question": "The typical installation of BTS3900 includes",
        "options": [
            "A) concrete floor",
            "B) stub fixed",
            "C) ESD floor",
            "D) sand ground installation"
        ],
        "answer": ["A) concrete floor", "C) ESD floor"]
    },
    
    {
        "question": "Which of the following statements of grounding is correct?",
        "options": [
            "A) First connect grounding cables when installation; unmount grounding cables at the end when Un-deployment",
            "B) Destroy grounding conductor is prohibit",
            "C) Operate device before installing grounding conductor is prohibit",
            "D) Device should ground with reliability"
        ],
        "answer": ["A) First connect grounding cables when installation; unmount grounding cables at the end when Un-deployment", "C) Operate device before installing grounding conductor is prohibit", "D) Device should ground with reliability"]
    },
    {
        "question": "Which of the following statements of GPS installation is correct?",
        "options": [
            "A) GPS antenna should install at the protect area of lighting rod(45 degree below the lighting rod top)",
            "B) Keep metal base horizon, use washer when need",
            "C) Fixing the GPS firmly, nothing block the vertical 90 degree area of the antenna",
            "D) Waterproof is needed at the connector between GPS antenna and feeder"
        ],
        "answer": ["A) GPS antenna should install at the protect area of lighting rod(45 degree below the lighting rod top)", "B) Keep metal base horizon, use washer when need", "C) Fixing the GPS firmly, nothing block the vertical 90 degree area of the antenna", "D) Waterproof is needed at the connector between GPS antenna and feeder"]
    },
    {
        "question": "Which of the following statements about PRRU installation is incorrect?",
        "options": [
            "A) Keep the equipment away from the room where there is water leaking or dripping.",
            "B) Do not install PRRU next to strong heat source equipment.",
            "C) The pRRU should be installed at least 50 cm away from heat sources or temperature-sensitive devices.",
            "D) The installation position, specifications, models, and supports of the antenna must meet the engineering design requirements."
        ],
        "answer": ["D) The installation position, specifications, models, and supports of the antenna must meet the engineering design requirements."]
    },
    
    {
        "question": "The cross-sectional area of the PGND cable of the FOIS300 outdoor cabinet is () The cross-sectional area of the AC power cable is not less than (A).",
        "options": [
            "A) 25mm2, 4mm2",
            "B) 25mm2, 6mm2",
            "C) 16mm2, 4mm2"
        ],
        "answer": ["A) 25mm2, 4mm2"]
    },
    {
        "question": "After unpacking a cabinet or BBU, you must power on the cabinet or BBU within (B) days.",
        "options": [
            "A) 1 day",
            "B) 7 days",
            "C) 14 days",
            "D) NA"
        ],
        "answer": ["B) 7 days"]
    },
    {
        "question": "The installation path ground cable should be ()",
        "options": [
            "A) As short as possible",
            "B) As long as possible",
            "C) No turning",
            "D) At least one turn"
        ],
        "answer": ["A) As short as possible"]
    },
    {
        "question": "Cables should be connected () to avoid water entering the junction box.",
        "options": [
            "A) Down to the top",
            "B) Up to the bottom",
            "C) Both sides",
            "D) Back"
        ],
        "answer": ["A) Down to the top"]
    },
    {
        "question": "Cables inside the cabinet must be routed according to the rules. () cables must be bundled to the cabinet.",
        "options": [
            "A) Left cabling",
            "B) Right cabling",
            "C) Far cabling",
            "D) Separate cabling on both sides of the cabinet"
        ],
        "answer": ["D) Separate cabling on both sides of the cabinet"]
    },
    {
        "question": "After excavation of foundation pit, the main content of trench inspection is to check ()",
        "options": [
            "A) Foundation Substrate soil",
            "B) Concrete cushion",
            "C) Construction safety",
            "D) Ambient environment"
        ],
        "answer": ["A) Foundation Substrate soil"]
    },
    {
        "question": "Which statements about the sealing of cable holes in the cabinet is unreasonable?",
        "options": [
            "A) All cable inlets and outlet holes of the cabinet must be closed.",
            "B) The cable openings of plastic parts must be properly cut.",
            "C) The cable openings of plastic parts must be neat and insulated.",
            "D) The cable holes on the cabinet can be properly closed to ensure ventilation of the cabinet."
        ],
        "answer": ["D) The cable holes on the cabinet can be properly closed to ensure ventilation of the cabinet."]
    },
    {
        "question": "The cable holes at the bottom of the outdoor cabinet need to be sealed with sealing materials. Which of the following is not a common sealing material?",
        "options": [
            "A) Silicone",
            "B) Oil sludge",
            "C) Cement"
        ],
        "answer": ["C) Cement"]
    },
    {
        "question": "Which of the following statements are correct about waterproofing the 3+3 connector of the RRU RF jumper?",
        "options": [
            "A) Step 1: Wrap three layers of waterproof tape on the connector.",
            "B) Step 2: Wrap three layers of PVC insulation tape.",
            "C) Step 3: Start binding cable ties to the cable at a position.",
            "D) All of the above are correct."
        ],
        "answer": ["A) Step 1: Wrap three layers of waterproof tape on the connector.", "B) Step 2: Wrap three layers of PVC insulation tape.", "C) Step 3: Start binding cable ties to the cable at a position."]
    },
    {
        "question": "Which statements about the removal of old equipment are correct?",
        "options": [
            "A) The old equipment must be intact.",
            "B) Use waterproof and dustproof materials to protect the ports.",
            "C) Old cables must be coiled and bundled separately.",
            "D) Old devices can be thrown away without recycling."
        ],
        "answer": ["A) The old equipment must be intact.", "B) Use waterproof and dustproof materials to protect the ports.", "C) Old cables must be coiled and bundled separately."]
    },
    
        {
            "question": "Which type of the transmission can be supported by WMPT board?",
            "options": ["A) E1/T1", "B) Electronic IP", "C) Optical IP", "D) Microwave"],
            "answer": ["A) E1/T1", "B) Electronic IP", "C) Optical IP"]  # Correct answers
        },
        
        {
            "question": "BBU3900’s functions include:",
            "options": [
                "A) Interactive communication between BTS and BSC", 
                "B) Provide the system clock", 
                "C) BTS Centralized Management", 
                "D) Provide the maintenance channel with LMT (or M2000)"
            ],
            "answer": ["A) Interactive communication between BTS and BSC", "B) Provide the system clock", "C) BTS Centralized Management", "D) Provide the maintenance channel with LMT (or M2000)"]  # All options are correct
        },
        {
            "question": "Option board of BBU3900 include:",
            "options": [
                "A) Power module UPEU", 
                "B) E1 surge protector UELP", 
                "C) Universal clock unit USCU", 
                "D) Environment monitor interface board UEIU"
            ],
            "answer": ["B) E1 surge protector UELP", "C) Universal clock unit USCU", "D) Environment monitor interface board UEIU"]  # Correct answers
        },
        {
            "question": "The typical installation of BTS3900 include:",
            "options": ["A) Concrete floor", "B) Stub fixed", "C) ESD floor", "D) Sand ground installation"],
            "answer": ["A) Concrete floor", "C) ESD floor"]  # Correct answers
        },
        {
            "question": "Which of the following statements of grounding is correct?",
            "options": [
                "A) First connect grounding cables when installation; unmount grounding cables at the end when Un-deployment", 
                "B) Destroy grounding conductor is prohibit", 
                "C) Operate device before installing grounding conductor is prohibit", 
                "D) Device should ground with reliability"
            ],
            "answer": ["A) First connect grounding cables when installation; unmount grounding cables at the end when Un-deployment", "C) Operate device before installing grounding conductor is prohibit", "D) Device should ground with reliability"]  # Correct answers
        },
        {
            "question": "Which of following statements of GPS installation is correct?",
            "options": [
                "A) GPS antenna should install at the protect area of lighting rod (45 degree below the lighting rod top)", 
                "B) Keep metal base horizon, use washer when need", 
                "C) Fixing the GPS firmly, nothing block the vertical 90 degree area of the antenna", 
                "D) Waterproof is needed at the connector between GPS antenna and feeder"
            ],
            "answer": ["A) GPS antenna should install at the protect area of lighting rod (45 degree below the lighting rod top)", "B) Keep metal base horizon, use washer when need", "C) Fixing the GPS firmly, nothing block the vertical 90 degree area of the antenna", "D) Waterproof is needed at the connector between GPS antenna and feeder"]  # All options are correct
        }
        
         
        
    ],
    "multiple_choice": [
        {
            "question": "The height of DCDU is:",
            "options": ["A) 1 U", "B) 2 U", "C) 3 U", "D) 4 U"],
            "answer": "A) 1 U"  # Correct answer
        },
        {
            "question": "What is the distance between each feeder cable clip?",
            "options": ["A) 1.5~2M", "B) 2~2.5M", "C) 2.5~3M", "D) 2~2.5M"],
            "answer": "A) 1.5~2M"  # Correct answer
        },
        {
            "question": "After the installation of BTS3900 cabinet, the vertical error should be less than:",
            "options": ["A) 2mm", "B) 3mm", "C) 4mm", "D) 5mm"],
            "answer": "B) 3mm"  # Correct answer
        },
        {
            "question": "Which cabinet is always used indoor?",
            "options": ["A) BTS3900", "B) BTS3900A", "C) APM30", "D) BTS3902E"],
            "answer": "A) BTS3900"  # Correct answer
        },
        {
            "question": "Which description is wrong as below?",
            "options": [
                "A) The jumper connectors must be protected before hoisting.",
                "B) The antenna and jumper cable can’t be hoisted together.",
                "C) Before hoisting the antenna, the hoisting rope bind on the upper antenna bracket, the steering rope bind on the lower antenna bracket.",
                "D) When hoisting the antenna, one group of people pulls the hoisting rope down, while another group pulls the steering rope away from the tower, preventing the antenna from hitting the tower."
            ],
            "answer": "B) The antenna and jumper cable can’t be hoisted together."  # Correct answer
        },
        {
            "question": "When pasting the indoor labels, keep _____ between the label and the end of the cable, and all directions must be consistent.",
            "options": ["A) 1-5mm", "B) 20-30mm", "C) 30-40mm", "D) 40-50mm"],
            "answer": "B) 20-30mm"  # Correct answer
        },
        {
            "question": "The jumper cable’s size of RRU commonly is:",
            "options": ["A) 1/4 inch", "B) 1/2 inch", "C) 5/4 inch", "D) 7/8 inch"],
            "answer": "B) 1/2 inch"  # Correct answer
        },
        {
            "question": "Usually, 2G antenna uses _____ RCU.",
            "options": ["A) 0", "B) 1", "C) 2", "D) 3"],
            "answer": "A) 0"  # Correct answer
        },
        {
            "question": "Making the OT terminal of the 16mm² grounding cable, the terminal’s type is:",
            "options": ["A) 12", "B) 14", "C) 15", "D) 16"],
            "answer": "B) 14"  # Correct answer
        },
        {
            "question": "The fiber work-temperature is _____, exceeding scope needs protection.",
            "options": ["A) -40°~60°", "B) -30°~60°", "C) -40°~50°", "D) -45°~70°"],
            "answer": "A) -40°~60°"  # Correct answer
        },
        {
            "question": "In Swap sites the transmission equipment will get power from:",
            "options": ["A) DCDU_BLVD", "B) DCDU_LLVD", "C) DC PDB", "D) AC PDB"],
            "answer": "A) DCDU_BLVD"  # Correct answer
        },
        {
            "question": "What is the function of RCU module in the antenna system?",
            "options": [
                "A) It receives and runs the control commands from the base station and drives the stepper motor.",
                "B) It is the passive component that couples RF signals or OK signals with feeder signals.",
                "C) It provides DC power supply and control commands through the feeder.",
                "D) It amplifies the weak signals received from the antenna to increase the receiver sensitivity of the base station system."
            ],
            "answer": "A) It receives and runs the control commands from the base station and drives the stepper motor."  # Correct answer
        },
        {
            "question": "Which of the following RF components can be used to remotely control the tilt of the antenna?",
            "options": ["A) Combiner", "B) BT", "C) RCU", "D) Divider"],
            "answer": "C) RCU"  # Correct answer
        },
        {
            "question": "Usually water-proof processing mode:",
            "options": [
                "A) 1 layer insulation tape, 3 layers waterproof rubber, 3 layers insulation tape, no bind direction requirement.",
                "B) 1 layer insulation tape, 3 layers waterproof rubber, 3 layers insulation tape, have bind direction requirement.",
                "C) 3 layers waterproof rubber, 3 layers insulation tape, no bind direction requirement.",
                "D) 3 layers waterproof rubber, have bind direction requirement."
            ],
            "answer": "B) 1 layer insulation tape, 3 layers waterproof rubber, 3 layers insulation tape, have bind direction requirement."  # Correct answer
        },
        {
            "question": "The correct requirement as below is:",
            "options": [
                "A) Before entering shelter from feeder window, IF/power cable and optic fiber ought to make waterproof bend.",
                "B) Before entering shelter from feeder window, only IF/power cable ought to make waterproof bend.",
                "C) Before entering shelter from feeder window, all cable (fiber) ought to make waterproof bend, and smaller bending radius is better.",
                "D) Before entering shelter from feeder window, except optic fiber, IF/power cable ought to make waterproof bend."
            ],
            "answer": "A) Before entering shelter from feeder window, IF/power cable and optic fiber ought to make waterproof bend."  # Correct answer
        },
        {
            "question": "The notes as below is wrong:",
            "options": [
                "A) All cables lay tidily and no crossing, the distance between power cable and optic fiber is beyond 3cm.",
                "B) Power cable and grounding cable ought to use the whole line, among which the connector is prohibited.",
                "C) Power cable and grounding cable ought to be connected correctly and fastening, install the elastic gasket, flat gasket and nut in proper order.",
                "D) OT terminal ought to be connected fastening, the connector should be insulated protection."
            ],
            "answer": "C) Power cable and grounding cable ought to be connected correctly and fastening, install the elastic gasket, flat gasket and nut in proper order."  # Correct answer
        },
        {
            "question": "The wrong explanation about jumping and IF cable:",
            "options": [
                "A) Jumping cable that is used for different sectors is connected with the main or standby channel correctly, and laid out tidily.",
                "B) Jumping cable for main channel is marked by double color ring, the one for standby is marked by single.",
                "C) 0–5 sector marking color order: red, orange, yellow, blue, purple, green.",
                "D) For minimum bending radius of jumping cable, the requirement that smaller is better is wrong."
            ],
            "answer": "C) 0–5 sector marking color order: red, orange, yellow, blue, purple, green."  # Correct answer
        },
        {
            "question": "The right explanation for cabinet insulation protection as below is:",
            "options": [
                "A) As the cabinet is connected with grounding system, no need to do the insulation protection.",
                "B) After cabinet foundation is installed, the foundation and expansion bolts’ resistance value should be more than 5 megohm.",
                "C) After cabinet foundation is installed, the foundation and expansion bolts’ resistance value should be less than 0.5 megohm.",
                "D) After cabinet foundation is installed, the foundation and expansion bolts’ resistance value should be more than 30 megohm."
            ],
            "answer": "B) After cabinet foundation is installed, the foundation and expansion bolts’ resistance value should be more than 5 megohm."  # Correct answer
        },
        {
            "question": "25 mm² grounding cable is made for OT terminal, which type of it can be selected?",
            "options": ["A) 20", "B) 22", "C) 24", "D) 25"],
            "answer": "B) 22"  # Correct answer
        },
        {
            "question": "Which cable will be connected first as the cabinet is installed?",
            "options": ["A) Power cable", "B) Signal line", "C) Transmission cable", "D) Grounding cable"],
            "answer": "D) Grounding cable"  # Correct answer
        },
        {
            "question": "BBU3900 DC input is:",
            "options": ["A) -48V", "B) -36V", "C) 220V", "D) 110V"],
            "answer": "A) -48V"  # Correct answer
        },
        {
            "question": "For wireless hardware installation, the wrong explanation is:",
            "options": [
                "A) After punching at cement floor for fixing cabinet foundation, vacuum sweeper is used to clean the dust.",
                "B) Electrostatic prevention hand ring should be worn as operating to pluck or insert the board in cabinet.",
                "C) The white ribbon should be used indoors.",
                "D) The hammer can be used for OT terminal fixing."
            ],
            "answer": "D) The hammer can be used for OT terminal fixing."  # Correct answer
        },
        {
            "question": "For equipment delivery and openness to check materials, the wrong explanation is:",
            "options": [
                "A) During the delivery and installation, the components and parts should be avoided to crash.",
                "B) Prohibit to touch the components’ surface with dirty gloves.",
                "C) Leave the equipment indoors after dismantling the package.",
                "D) If equipment package is broken, soaking or deformed, should dismantle the package and confirm the equipment is OK or not."
            ],
            "answer": "D) If equipment package is broken, soaking or deformed, should dismantle the package and confirm the equipment is OK or not."  # Correct answer
        },
        {
            "question": "Which of the following statements about bending radius is wrong?",
            "options": [
                "A) 7/8\" feeder above 250mm, 5/4\" feeder above 380mm.",
                "B) 1/4\" jumper above 35mm, 1/2\" jumper (super flexible) above 50mm, 1/2\" jumper (normal) above 127mm.",
                "C) The bending radius of power/grounding cable no less than 3-5 times of its diameter.",
                "D) Bending radius of signal cable no less than twice of its diameter."
            ],
            "answer": "D) Bending radius of signal cable no less than twice of its diameter."  # Correct answer
        },
        {
            "question": "Height of BBU3900 is:",
            "options": ["A) 1 U", "B) 2 U", "C) 3 U", "D) 4 U"],
            "answer": "B) 2 U"  # Correct answer
        },
        {
            "question": "Which of the following protective actions is wrong?",
            "options": [
                "A) Paste insulation tape at the incision.",
                "B) Protect action is needed where fiber goes out of the cabinet, to prevent from squeeze and bite.",
                "C) Tie the fiber terminal when lifting and installing the RRU.",
                "D) Clear define the specification of using fiber tube."
            ],
            "answer": "C) Tie the fiber terminal when lifting and installing the RRU."  # Correct answer
        },
        {
            "question": "RRU has how many grounding points?",
            "options": ["A) 1", "B) 2", "C) 3", "D) 4"],
            "answer": "B) 2"  # Correct answer
        },
        {
            "question": "At how many points is the IF cable grounding done?",
            "options": ["A) 1", "B) 2", "C) 3", "D) 4"],
            "answer": "B) 2"  # Correct answer
        }
    ]
}
# Flatten questions for navigation
if not st.session_state.flattened_questions:
    flattened_questions = []

    for category, qs in QAC.items():
        for q in qs:
            q['type'] = category  # Set the type for each question
            flattened_questions.append(q)

    # Shuffle questions within each type
    random.shuffle(flattened_questions)

    true_false_questions = [q for q in flattened_questions if q['type'] == 'true_false']
    choose_correct_questions = [q for q in flattened_questions if q['type'] == 'choose_correct']
    mcq_questions = [q for q in flattened_questions if q['type'] == 'multiple_choice']

    # Combine the questions in the desired order
    all_questions = (
    true_false_questions[:15] + 
    choose_correct_questions[:10] + 
    mcq_questions[:15]
)

    # Limit to the first 40 questions
    st.session_state.flattened_questions = all_questions[:40]

# Initialize answers
if len(st.session_state.answers) != len(st.session_state.flattened_questions):
    st.session_state.answers = [None] * len(st.session_state.flattened_questions)


# Login form
if not st.session_state.logged_in:
    st.header("Welcome to Huawei Quiz Portal")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")  # You might want to handle password validation separately

    if st.button("Login"):
        if username in allowed_usernames and password:  # Add password validation as needed
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.start_time = datetime.now()  # Track start time on login
            st.success("Logged in successfully!")
            st.experimental_rerun()  # Refresh the page to reflect the new state
        else:
            st.error("Please enter a valid username and password.")
else:
    st.sidebar.markdown(f"## Welcome **{st.session_state.username}** For The Quiz Of EHS Assurance ")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.current_question = 0  # Reset current question
        st.session_state.answers = [None] * len(st.session_state.flattened_questions)  # Reset answers
        st.session_state.username = ""
        st.session_state.quiz_submitted = False  # Reset quiz submission status
        st.session_state.flattened_questions = []  # Reset questions
        st.success("You have been logged out.")
        st.experimental_rerun()  # Refresh the page to reflect the new state

    # Quiz Page
    st.header(f"Welcome {st.session_state.username} For The Quiz Of Quality Standards and SOPs")

    
    # Navigation buttons
    col1, col2 = st.columns(2)

    # Only show navigation buttons if the quiz hasn't been submitted
    if not st.session_state.quiz_submitted:
        if st.session_state.current_question > 0:
            with col1:
                if st.button("Previous", key="prev"):
                    st.session_state.current_question -= 1

    if st.session_state.current_question < len(st.session_state.flattened_questions) - 1:  # Show "Next" button if not on the last question
        with col2:
            if st.button("Next", key="next"):
                st.session_state.current_question += 1

    if st.session_state.current_question == len(st.session_state.flattened_questions) - 1 and not st.session_state.quiz_submitted:
        if st.button("Submit", key="submit"):
            if not st.session_state.quiz_submitted:  # Only process if not already submitted
                total_score = 0
                questions_attempted = 0
                correct_answers = 0
                wrong_answers = 0
                result_details = []

                for idx, question_detail in enumerate(st.session_state.flattened_questions):
                    user_answer = st.session_state.answers[idx]
                    if user_answer is not None:
                        questions_attempted += 1
                        
                        if question_detail["type"] == "true_false":
                            
                            score = 2
                            if user_answer == question_detail["answer"]:
                                correct_answers += 1
                                total_score += score
                                result_details.append((question_detail["question"], user_answer, question_detail["answer"], "Correct"))
                            else:
                                wrong_answers += 1
                                result_details.append((question_detail["question"], user_answer, question_detail["answer"], "Wrong"))
                        elif question_detail["type"] == "choose_correct":
                            score = 4
                            if sorted(user_answer) == sorted(question_detail["answer"]):
                                correct_answers += 1
                                total_score += score
                                result_details.append((question_detail["question"], user_answer, question_detail["answer"], "Correct"))
                            else:
                                wrong_answers += 1
                                result_details.append((question_detail["question"], user_answer, question_detail["answer"], "Wrong"))
                        elif question_detail["type"] == "multiple_choice":
                            score = 2
                            if user_answer == question_detail["answer"]:
                                correct_answers += 1
                                total_score += score
                                result_details.append((question_detail["question"], user_answer, question_detail["answer"], "Correct"))
                            else:
                                wrong_answers += 1
                                result_details.append((question_detail["question"], user_answer, question_detail["answer"], "Wrong"))

                end_time = datetime.now()
                time_taken = end_time - st.session_state.start_time
                
                save_results(st.session_state.username, questions_attempted, correct_answers, wrong_answers, total_score, str(time_taken), str(result_details))
                st.success("Quiz submitted successfully!")
                st.session_state.quiz_submitted = True

                total_marks = 100  # Total marks for the quiz
                percentage = (total_score / total_marks) * 100
                result_message = "<h1 style='color: green;'>Congratulations! You passed the Test!</h1>" if percentage >= 70 else "<h1 style='color: red;'>Sorry You Have Failed The Test!.</h1>"

                # Display results in a card
                st.markdown("<div class='card'><h3>Quiz Results</h3>", unsafe_allow_html=True)
                st.markdown(result_message, unsafe_allow_html=True)
                st.write(f"**Total Questions Attempted:** {questions_attempted}")
                st.write(f"**Correct Answers:** {correct_answers}")
                st.write(f"**Wrong Answers:** {wrong_answers}")
                st.write(f"**Total Score:** {total_score}")
                st.write(f"**Percentage:** {percentage:.2f}%")
                st.markdown("</div>", unsafe_allow_html=True)

    # CSS for enhanced design
    st.markdown("""<style>
        .card {
            background-color: #ffcccc; /* Light background */
            border: 1px solid #ddd; /* Subtle border */
            border-radius: 8px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .question-card {
            background-color: #ffcccc; /* Light red color for questions */
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
    </style>""", unsafe_allow_html=True)

    # Display current question if quiz is not submitted
    if not st.session_state.quiz_submitted and st.session_state.current_question < len(st.session_state.flattened_questions):
        current_question = st.session_state.flattened_questions[st.session_state.current_question]
        total_questions = 40
        question_number = st.session_state.current_question + 1 
        progress_percentage = question_number / total_questions
        # Display question count and progress bar
        st.write(f"**Question {question_number} of {total_questions}**")  # Question count
        st.progress(progress_percentage)
        
        st.markdown(f"<div class='question-card'><h4>Question {question_number}: {current_question['question']}</h4></div>", unsafe_allow_html=True)

        # Display options based on question type
        if current_question["type"] == "multiple_choice":
            st.header('Multiple Choice Questions')
            st.session_state.answers[st.session_state.current_question] =  st.radio("Choose an option:", current_question["options"], key=f"mc_{st.session_state.current_question}")
        elif current_question["type"] == "true_false":
            st.header('True False')
         
            st.session_state.answers[st.session_state.current_question] =st.radio("Choose an option:", ["True", "False"], key=f"tf_{st.session_state.current_question}")
        elif current_question["type"] == "choose_correct":
            st.header('Choose The Correct')
           
            st.session_state.answers[st.session_state.current_question] =st.multiselect("Choose correct options:", current_question["options"], key=f"cc_{st.session_state.current_question}")

# Add a footer
st.markdown("<footer style='text-align: center; margin-top: 20px;'>© 2024 Huawei Training Portal. All Rights Reserved.</footer>", unsafe_allow_html=True)
