"use client";

import { useState, useEffect } from "react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { db } from "@/lib/firebaseConfig";
import { ref, push, onValue, get, set } from "firebase/database";
import { CloudCog } from "lucide-react";
import { useRouter } from "next/navigation";

export default function AuthPage() {
  // State for Registration
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [license, setLicense] = useState("");
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<"login" | "register">("login");

  // State for Login
  const [loginEmail, setLoginEmail] = useState("");
  const [loginLicense, setLoginLicense] = useState("");

  // Store Registered Doctors
  const [doctors, setDoctors] = useState<{ email: string; license: string; name: string }[]>([]);

  // Fetch doctors from the database
  useEffect(() => {
    const doctorsRef = ref(db, "doctors");
    onValue(doctorsRef, (snapshot) => {
      const data = snapshot.val();
      if (data) {
        setDoctors(Object.values(data));
      } else {
        setDoctors([]);
      }
    });
  }, []);

  // Handle Registration (Store Doctor Info)
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
  
    try {
      // Store doctor details using license number as the key
      await set(ref(db, `doctors/${license}`), { name, email, license });
  
      alert("Doctor Registered Successfully!");
      setName("");
      setEmail("");
      setLicense("");
      setActiveTab("login")
    } catch (error) {
      console.error(error);
      alert("Error Registering Doctor.");
    }
  };
  

  // Handle Login (Check if Doctor Exists)
  
    const handleLogin = async (e: React.FormEvent) => {
      e.preventDefault();
      
      try {
        // Reference to the doctor's data by license number
        const doctorRef = ref(db, `doctors/${loginLicense}`);
        
        // Fetch the data
        const snapshot = await get(doctorRef);
        
        if (snapshot.exists()) {
          const doctorData = snapshot.val();
          
          // Verify if the email matches
          if (doctorData.email === loginEmail) {
            alert("Login Successful!");
            setLoginEmail("");
            setLoginLicense("");
            router.push("/add-user");
          } else {
            alert("Incorrect email. Please try again.");
          }
        } else {
          alert("Doctor not found. Please check credentials.");
        }
      } catch (error) {
        console.error("Error logging in:", error);
        alert("An error occurred during login.");
      }
    };


  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100 p-4">
      <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-lg">
        <Tabs defaultValue="login">
          {/* Tabs Navigation */}
          <TabsList className="flex w-full">
            <TabsTrigger value="login" className="w-1/2">Login</TabsTrigger>
            <TabsTrigger value="register" className="w-1/2">Register</TabsTrigger>
          </TabsList>

          {/* Login Form */}
          <TabsContent value="login">
            <h2 className="text-xl font-bold text-center mt-4">Doctor Login</h2>
            <form onSubmit={handleLogin} className="space-y-4 mt-4">
              <div>
                <Label htmlFor="loginEmail">Email</Label>
                <Input 
                  id="loginEmail"
                  type="email"
                  placeholder="Enter your email"
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  required
                />
              </div>
              <div>
                <Label htmlFor="loginLicense">Password</Label>
                <Input 
                  id="loginLicense"
                  type="text"
                  placeholder="Enter your license number"
                  value={loginLicense}
                  onChange={(e) => setLoginLicense(e.target.value)}
                  required
                />
              </div>
              <Button type="submit" className="w-full">Login</Button>
            </form>
          </TabsContent>

          {/* Registration Form */}
          <TabsContent value="register">
            <h2 className="text-xl font-bold text-center mt-4">Doctor Registration</h2>
            <form onSubmit={handleRegister} className="space-y-4 mt-4">
              <div>
                <Label htmlFor="name">Full Name</Label>
                <Input 
                  id="name"
                  type="text"
                  placeholder="Enter your full name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>
              <div>
                <Label htmlFor="registerEmail">Email</Label>
                <Input 
                  id="registerEmail"
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <div>
                <Label htmlFor="license">Medical License Number</Label>
                <Input 
                  id="license"
                  type="text"
                  placeholder="Enter your license number"
                  value={license}
                  onChange={(e) => setLicense(e.target.value)}
                  required
                />
              </div>
              <Button type="submit" className="w-full">Register</Button>
            </form>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
