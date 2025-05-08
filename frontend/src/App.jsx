import { useState } from 'react'
import {Routes, Route} from 'react-router'
import './App.css'
import Home from './components/Home';
import Create from './components/Create'
import Edit from './components/Edit'
import Delete from './components/Delete'
import Navbar from './components/navbar/Navbar'
import Manager from './components/Manager'
import Volunteer from './components/Volunteer'
import Workflows from './components/Workflows';
import Tasks from './components/Tasks';
import Analytics from './components/Analytics';
import Notifications from './components/Notifications';
// import Logs from './components/Logs';
import Settings from './components/Settings';
import Help from './components/Help';





function App() {
  return (
    <>
    <Navbar
    content={
      <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/manager" element={<Manager/>}/>
      <Route path="/volunteer" element={<Volunteer/>}/>
      <Route path="/create" element={<Create/>}/>
      <Route path="/manager/edit/:id" element={<Edit/>}/>
      <Route path="/manager/delete/:id" element={<Delete/>}/>
      {/* New routes for sidebar sections */}
      <Route path="/workflows" element={<Workflows />} />
      <Route path="/tasks" element={<Tasks />} />
      <Route path="/analytics" element={<Analytics />} />
      <Route path="/notifications" element={<Notifications />} />
      {/* <Route path="/logs" element={<Logs />} /> */}
      <Route path="/settings" element={<Settings />} />
      <Route path="/help" element={<Help />} />
  </Routes>
    }
    />
      
    </>
  )
}

export default App