"use client";

import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Calendar } from "@/components/ui/calendar"; // Add a calendar component
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"; // For calendar popover
import { format } from "date-fns"; // For formatting dates
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"; // For dropdowns
import { v4 as uuidv4 } from "uuid";
import { ref, set } from "firebase/database";
import { db } from "../../lib/firebaseConfig";
import { useRouter } from "next/navigation";

const sections = [
  { id: "personal-info", label: "Personal Information" },
  { id: "report-info", label: "Report Information" },
  { id: "medical-history", label: "Medical History" },
  { id: "additional-reports", label: "Additional Reports" },
];

export default function MedicalForm() {
  const [activeSection, setActiveSection] = useState("personal-info");
  const [pdfFiles, setPdfFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [responseData, setResponseData] = useState(null);
  const [formData, setFormData] = useState({
    personalInfo: {
      firstName: "",
      middleName: "",
      lastName: "",
      dob: null,
      bloodGroup: "",
      gender: "",
    },
    reportInfo: {
      reportDate: null,
      practitionerName: "",
      clinicName: "",
      address: "",
    },
    medicalHistory: {
      medicalHistory: "",
      familyHistory: "",
      socialHistory: "",
    },
  });

  // Handle file selection
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setPdfFiles([...pdfFiles, ...Array.from(event.target.files)]);
    }
  };

  // Upload PDF to backend
  const handleUpload = async () => {
    if (pdfFiles.length === 0) {
      alert("Please select at least one PDF file.");
      return;
    }

    const formData = new FormData();
    pdfFiles.forEach((file) => {
      formData.append("document", file);
    });

    try {
      setIsUploading(true);

      const response = await fetch("https://healthbot.pythonanywhere.com/api/upload-report/", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || "Failed to upload PDFs.");
      }

      const data = await response.json();
      setResponseData(JSON.parse(data.summary)); // Parse the JSON string
      alert("PDFs uploaded successfully!");
      setPdfFiles([]); // Clear selected files
    } catch (error: any) {
      console.error("Error uploading PDFs:", error);
      alert(error.message);
    } finally {
      setIsUploading(false);
    }
  };

  // Save all data to Firebase
  const saveToFirebase = async () => {
    const hid = uuidv4(); // Generate a unique ID for the user

    // Combine all form data and server response (if available)
    const userData = {
      ...formData,
      additionalReports: responseData || null, // Include server response if it exists
    };

    try {
      // Save data to Firebase under `user/{hid}`
      await set(ref(db, `user/${hid}`), userData);
      alert("Data saved to Firebase successfully!");
    } catch (error) {
      console.error("Error saving data to Firebase:", error);
      alert("Failed to save data to Firebase.");
    }
  };

  // Recursive function to render nested data in a table
  const renderTableData = (data: any) => {
    if (typeof data === "object" && !Array.isArray(data)) {
      return (
        <Table>
          <TableBody>
            {Object.entries(data).map(([key, value]) => (
              <TableRow key={key}>
                <TableCell className="font-medium">{key}</TableCell>
                <TableCell>{renderTableData(value)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      );
    } else if (Array.isArray(data)) {
      return (
        <ul className="list-disc list-inside">
          {data.map((item, index) => (
            <li key={index}>{renderTableData(item)}</li>
          ))}
        </ul>
      );
    } else {
      return <span>{data}</span>;
    }
  };

  // Track scrolling to update active section
  useEffect(() => {
    const handleScroll = () => {
      let currentSection = "";
      sections.forEach((section) => {
        const element = document.getElementById(section.id);
        if (element) {
          const rect = element.getBoundingClientRect();
          if (rect.top <= 150 && rect.bottom >= 150) {
            currentSection = section.id;
          }
        }
      });
      if (currentSection) setActiveSection(currentSection);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);
  const router = useRouter();
  return (
    <div className="flex h-screen"> 
      {/* Sidebar Navigation */}
      <aside className="w-1/4 p-4 border-r sticky top-0 h-screen overflow-auto">
        <div className="flex flex-col space-y-2">
          {sections.map((section) => (
            <Button
              key={section.id}
              variant={activeSection === section.id ? "default" : "outline"}
              onClick={() => {
                document.getElementById(section.id)?.scrollIntoView({ behavior: "smooth" });
                setActiveSection(section.id);
              }}
              className={cn("w-full", activeSection === section.id && "bg-blue-500 text-white")}
            >
              {section.label}
            </Button>
          ))}
          <div>
            <button className="p-2 text-black font-semibold text-center border-2 border-black w-full" onClick={()=>router.push("/analysis")}>View Realtime Analysis</button>
          </div>
        </div>
        
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-6 overflow-y-auto">
        <div className="text-center text-2xl font-semibold mb-6">
          REGISTER-USER
        </div>
        {sections.map((section) => (
          <Card key={section.id} id={section.id} className="mb-6">
            <CardContent className="p-4">
              <h2 className="text-xl font-semibold">{section.label}</h2>
              {section.id === "personal-info" && (
                <>
                  <div className="grid grid-cols-3 gap-4 mt-4">
                    <div>
                      <Label>First Name</Label>
                      <Input
                        placeholder="John"
                        value={formData.personalInfo.firstName}
                        onChange={(e) =>
                          setFormData((prev) => ({
                            ...prev,
                            personalInfo: { ...prev.personalInfo, firstName: e.target.value },
                          }))
                        }
                      />
                    </div>
                    <div>
                      <Label>Middle Name</Label>
                      <Input
                        placeholder="Doe"
                        value={formData.personalInfo.middleName}
                        onChange={(e) =>
                          setFormData((prev) => ({
                            ...prev,
                            personalInfo: { ...prev.personalInfo, middleName: e.target.value },
                          }))
                        }
                      />
                    </div>
                    <div>
                      <Label>Last Name</Label>
                      <Input
                        placeholder="Smith"
                        value={formData.personalInfo.lastName}
                        onChange={(e) =>
                          setFormData((prev) => ({
                            ...prev,
                            personalInfo: { ...prev.personalInfo, lastName: e.target.value },
                          }))
                        }
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-4 mt-4">
                    <div>
                      <Label>Date of Birth</Label>
                      <Popover>
                        <PopoverTrigger asChild>
                          <Button variant="outline" className="w-full">
                            {formData.personalInfo.dob
                              ? format(formData.personalInfo.dob, "PPP")
                              : "Pick a date"}
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-auto p-0">
                          <Calendar
                            mode="single"
                            selected={formData.personalInfo.dob}
                            onSelect={(date:any) =>
                              setFormData((prev) => ({
                                ...prev,
                                personalInfo: { ...prev.personalInfo, dob: date },
                              }))
                            }
                          />
                        </PopoverContent>
                      </Popover>
                    </div>
                    <div>
                      <Label>Blood Group</Label>
                      <Select
                        value={formData.personalInfo.bloodGroup}
                        onValueChange={(value:any) =>
                          setFormData((prev) => ({
                            ...prev,
                            personalInfo: { ...prev.personalInfo, bloodGroup: value },
                          }))
                        }
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select blood group" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="A+">A+</SelectItem>
                          <SelectItem value="A-">A-</SelectItem>
                          <SelectItem value="B+">B+</SelectItem>
                          <SelectItem value="B-">B-</SelectItem>
                          <SelectItem value="O+">O+</SelectItem>
                          <SelectItem value="O-">O-</SelectItem>
                          <SelectItem value="AB+">AB+</SelectItem>
                          <SelectItem value="AB-">AB-</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label>Gender</Label>
                      <Select
                        value={formData.personalInfo.gender}
                        onValueChange={(value:any) =>
                          setFormData((prev) => ({
                            ...prev,
                            personalInfo: { ...prev.personalInfo, gender: value },
                          }))
                        }
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select gender" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Male">Male</SelectItem>
                          <SelectItem value="Female">Female</SelectItem>
                          <SelectItem value="Other">Other</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </>
              )}

              {section.id === "report-info" && (
                <>
                  <div className="mt-4">
                    <Label>Report Generated Date</Label>
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button variant="outline" className="w-full">
                          {formData.reportInfo.reportDate
                            ? format(formData.reportInfo.reportDate, "PPP")
                            : "Pick a date"}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0">
                        <Calendar
                          mode="single"
                          selected={formData.reportInfo.reportDate}
                          onSelect={(date:any) =>
                            setFormData((prev) => ({
                              ...prev,
                              reportInfo: { ...prev.reportInfo, reportDate: date },
                            }))
                          }
                        />
                      </PopoverContent>
                    </Popover>
                  </div>
                  <div className="grid grid-cols-2 gap-4 mt-4">
                    <div>
                      <Label>Practitioner Name</Label>
                      <Input
                        placeholder="Dr. Jane Doe"
                        value={formData.reportInfo.practitionerName}
                        onChange={(e) =>
                          setFormData((prev) => ({
                            ...prev,
                            reportInfo: { ...prev.reportInfo, practitionerName: e.target.value },
                          }))
                        }
                      />
                    </div>
                    <div>
                      <Label>Clinic Name</Label>
                      <Input
                        placeholder="Health Clinic"
                        value={formData.reportInfo.clinicName}
                        onChange={(e) =>
                          setFormData((prev) => ({
                            ...prev,
                            reportInfo: { ...prev.reportInfo, clinicName: e.target.value },
                          }))
                        }
                      />
                    </div>
                  </div>
                  <div className="mt-4">
                    <Label>Address</Label>
                    <Textarea
                      placeholder="123 Main St, City, Country"
                      value={formData.reportInfo.address}
                      onChange={(e) =>
                        setFormData((prev) => ({
                          ...prev,
                          reportInfo: { ...prev.reportInfo, address: e.target.value },
                        }))
                      }
                    />
                  </div>
                </>
              )}

              {section.id === "medical-history" && (
                <>
                  <div className="mt-4">
                    <Label>Medical History</Label>
                    <Textarea
                      placeholder="Hypertension, Diabetes, etc."
                      value={formData.medicalHistory.medicalHistory}
                      onChange={(e) =>
                        setFormData((prev) => ({
                          ...prev,
                          medicalHistory: { ...prev.medicalHistory, medicalHistory: e.target.value },
                        }))
                      }
                    />
                  </div>
                  <div className="mt-4">
                    <Label>Family History</Label>
                    <Textarea
                      placeholder="Family history of diseases"
                      value={formData.medicalHistory.familyHistory}
                      onChange={(e) =>
                        setFormData((prev) => ({
                          ...prev,
                          medicalHistory: { ...prev.medicalHistory, familyHistory: e.target.value },
                        }))
                      }
                    />
                  </div>
                  <div className="mt-4">
                    <Label>Social History</Label>
                    <Textarea
                      placeholder="Smoking, alcohol consumption, etc."
                      value={formData.medicalHistory.socialHistory}
                      onChange={(e) =>
                        setFormData((prev) => ({
                          ...prev,
                          medicalHistory: { ...prev.medicalHistory, socialHistory: e.target.value },
                        }))
                      }
                    />
                  </div>
                </>
              )}

              {section.id === "additional-reports" && (
                <>
                  <div className="mt-4">
                    <Label>Upload PDF Reports</Label>
                    <Input
                      type="file"
                      accept=".pdf"
                      multiple
                      onChange={handleFileChange}
                      className="mt-2"
                    />
                  </div>
                  {pdfFiles.length > 0 && (
                    <div className="mt-4">
                      <h3 className="font-semibold">Selected Files:</h3>
                      <ul className="list-disc list-inside">
                        {pdfFiles.map((file, index) => (
                          <li key={index} className="text-sm">{file.name}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  <Button onClick={handleUpload} className="mt-4" disabled={isUploading}>
                    {isUploading ? "Uploading..." : "Upload Reports"}
                  </Button>

                  {/* Display parsed data in a table */}
                  {responseData && (
                    <div className="mt-6">
                      <h3 className="text-xl font-semibold mb-4">Report Summary</h3>
                      <div className="bg-gray-100 p-4 rounded-lg">
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead>Category</TableHead>
                              <TableHead>Details</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {Object.entries(responseData).map(([key, value]) => (
                              <TableRow key={key}>
                                <TableCell className="font-medium">{key}</TableCell>
                                <TableCell>{renderTableData(value)}</TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </div>
                    </div>
                  )}
                </>
              )}
            </CardContent>
          </Card>
        ))}

        {/* Save to Firebase Button */}
        <div className="mt-6">
          <Button onClick={saveToFirebase} className="w-full">
            Save Data
          </Button>
        </div>
      </main>
    </div>
  );
}