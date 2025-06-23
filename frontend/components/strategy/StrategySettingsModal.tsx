import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { apiClient } from "@/services/api";
import {
  Settings,
  Save,
  AlertTriangle,
  Trash2
} from "lucide-react";

interface StrategySettingsModalProps {
  strategy: {
    id: string;
    name: string;
    type: string;
    risk_level: string;
    created_at: string;
  };
  onClose: () => void;
  onDelete: (strategyId: string) => Promise<void>;
}

export function StrategySettingsModal({ 
  strategy, 
  onClose,
  onDelete
}: StrategySettingsModalProps) {
  const [strategyName, setStrategyName] = useState(strategy.name);
  const [riskLevel, setRiskLevel] = useState(strategy.risk_level);
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [message, setMessage] = useState("");
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const handleSaveSettings = async () => {
    setIsSaving(true);
    setMessage("");
    
    try {
      const response = await apiClient.updateStrategy({
        id: strategy.id,
        name: strategyName,
        risk_level: riskLevel
      });
      
      if (response.success) {
        setMessage("Strategy settings updated successfully!");
        // Clear message after 3 seconds
        setTimeout(() => setMessage(""), 3000);
      } else {
        setMessage(`Error: ${response.error || "Failed to update strategy"}`);
      }
    } catch (error) {
      setMessage("An error occurred while saving settings");
    } finally {
      setIsSaving(false);
    }
  };

  const handleConfirmDelete = async () => {
    setIsDeleting(true);
    try {
      await onDelete(strategy.id);
      // Close both the dialog and the modal
      setShowDeleteConfirm(false);
      onClose();
    } catch (error) {
      setMessage("Failed to delete strategy. Please try again.");
      setShowDeleteConfirm(false);
    } finally {
      setIsDeleting(false);
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case "conservative": return "secondary";
      case "moderate": return "default";
      case "aggressive": return "destructive";
      default: return "default";
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <Card className="w-full max-w-md">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <Settings className="h-5 w-5 text-gray-600" />
            <CardTitle>Strategy Settings</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium">Strategy Name</label>
            <Input
              value={strategyName}
              onChange={(e) => setStrategyName(e.target.value)}
              className="mt-1"
            />
          </div>
          
          <div>
            <label className="text-sm font-medium">Strategy Type</label>
            <div className="mt-1 flex items-center">
              <Badge variant="outline" className="text-gray-700">
                {strategy.type}
              </Badge>
              <span className="text-xs text-gray-500 ml-2">(Cannot be changed)</span>
            </div>
          </div>
          
          <div>
            <label className="text-sm font-medium">Risk Level</label>
            <div className="grid grid-cols-3 gap-2 mt-1">
              {["conservative", "moderate", "aggressive"].map((risk) => (
                <Button
                  key={risk}
                  type="button"
                  variant={riskLevel === risk ? "default" : "outline"}
                  className={`capitalize ${riskLevel === risk ? "text-white" : ""}`}
                  onClick={() => setRiskLevel(risk)}
                >
                  {risk}
                </Button>
              ))}
            </div>
          </div>

          {message && (
            <div className={`p-3 rounded-md ${message.includes("Error") ? "bg-red-50 text-red-700" : "bg-green-50 text-green-700"}`}>
              {message}
            </div>
          )}
          
          <div className="flex justify-between pt-2">
            <Button 
              variant="destructive" 
              onClick={() => setShowDeleteConfirm(true)}
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Delete Strategy
            </Button>
            
            <div className="space-x-2">
              <Button variant="outline" onClick={onClose}>
                Cancel
              </Button>
              <Button 
                onClick={handleSaveSettings} 
                disabled={isSaving || !strategyName.trim()}
              >
                <Save className="h-4 w-4 mr-2" />
                Save Changes
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Custom Delete Confirmation Dialog without using Alert Dialog component */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <div className="flex items-center space-x-2">
                <AlertTriangle className="h-5 w-5 text-red-500" />
                <CardTitle>Delete Strategy</CardTitle>
              </div>
              <p className="text-sm text-gray-600 mt-2">
                Are you sure you want to delete "{strategy.name}"? This action cannot be undone.
              </p>
            </CardHeader>
            <CardContent>
              <div className="flex justify-end space-x-3">
                <Button 
                  variant="outline" 
                  onClick={() => setShowDeleteConfirm(false)}
                  disabled={isDeleting}
                >
                  Cancel
                </Button>
                <Button 
                  variant="destructive"
                  onClick={handleConfirmDelete}
                  disabled={isDeleting}
                  className="bg-red-600 hover:bg-red-700"
                >
                  {isDeleting ? "Deleting..." : "Delete Strategy"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}